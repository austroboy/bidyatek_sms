import logging
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from decimal import Decimal
from .models import PaymentTransaction, SSLC, TrustBank, BankDisbursementAccount, FeeHeadBankDistribution
from crucial.models import *
from sslcommerz_lib import SSLCOMMERZ 
from accounting.models import *
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.utils.timezone import make_aware

logger = logging.getLogger(__name__)

# ====================
# PAYMENT INITIATION
# ====================

# @csrf_exempt
# @login_required
# def initiate_payment(request):
#     if not request.user.is_authenticated:
#         return redirect('/login/')
    
#     user = request.user
#     student_profile = user.student_profile.first()
#     if not student_profile:
#         return render(request, 'ssl_commerz/error.html', {'error': 'No student profile found.'})

#     unpaid_fees = Fees.objects.filter(student_id=student_profile).exclude(status='paid')
#     total_amount = sum(fee.total_fee_after_partial_payments() for fee in unpaid_fees)

#     if total_amount <= Decimal('0.00'):
#         return render(request, 'ssl_commerz/error.html', {'error': 'No unpaid fees.'})

#     if request.method == 'POST':
#         payment_method = request.POST.get('payment_method', 'sslcommerz')
        
#         # Check if Trust Bank is active
#         if payment_method == 'trustbank':
#             trust_config = TrustBank.objects.first()
#             if not trust_config or not trust_config.is_active:
#                 return render(request, 'ssl_commerz/error.html', {'error': 'Trust Bank payment is not available.'})
        
#         tran_id = f"TXN_{user.id}_{int(time.time())}"
        
#         transaction = PaymentTransaction.objects.create(
#             user=user,
#             student_profile=student_profile,
#             tran_id=tran_id,
#             amount=total_amount,
#             status='PENDING',
#             gateway=payment_method
#         )
        
#         # If admin, redirect to disbursement setup
#         if request.user.is_staff:
#             return redirect('ssl_commerz:admin_disbursement_setup', tran_id=tran_id)
        
#         # Regular student flow (without disbursement)
#         parent_profile = student_profile.parent_id.parent_profile if student_profile.parent_id else None
#         parent_phone = "N/A"
#         if parent_profile and parent_profile.g_mobile_no:
#             parent_phone = parent_profile.g_mobile_no
#         elif student_profile.student_field.phone_number:  
#             parent_phone = student_profile.student_field.phone_number 

#         if payment_method == 'trustbank':
#             return handle_trust_payment(request, transaction, total_amount, parent_phone, user)
#         else:
#             return handle_sslcommerz_payment_without_disbursement(request, transaction, total_amount, student_profile, parent_phone)
    
#     # Check if Trust Bank is active
#     trust_config = TrustBank.objects.first()
#     trust_active = trust_config.is_active if trust_config else False
    
#     return render(request, 'ssl_commerz/payment.html', {
#         'total_amount': total_amount,
#         'unpaid_fees': unpaid_fees,
#         'trust_active': trust_active
#     })


@csrf_exempt
@login_required
def initiate_payment(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    
    user = request.user
    student_profile = user.student_profile.first()
    if not student_profile:
        return render(request, 'ssl_commerz/error.html', {'error': 'No student profile found.'})

    unpaid_fees = Fees.objects.filter(student_id=student_profile).exclude(status='paid')
    total_amount = sum(fee.total_fee_after_partial_payments() for fee in unpaid_fees)

    if total_amount <= Decimal('0.00'):
        return render(request, 'ssl_commerz/error.html', {'error': 'No unpaid fees.'})

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'sslcommerz')
        
        # Check if Trust Bank is active
        if payment_method == 'trustbank':
            trust_config = TrustBank.objects.first()
            if not trust_config or not trust_config.is_active:
                return render(request, 'ssl_commerz/error.html', {'error': 'Trust Bank payment is not available.'})
        
        tran_id = f"TXN_{user.id}_{int(time.time())}"
        
        transaction = PaymentTransaction.objects.create(
            user=user,
            student_profile=student_profile,
            tran_id=tran_id,
            amount=total_amount,
            status='PENDING',
            gateway=payment_method
        )
        
        # ============================================================
        # AUTOMATIC DISBURSEMENT SETUP FOR STUDENTS
        # ============================================================
        if not request.user.is_staff:
            # For student payments, automatically set up disbursement based on FeeHeadBankDistribution
            try:
                disbursement_data = generate_automatic_disbursement_data(student_profile, total_amount)
                if disbursement_data:
                    transaction.disbursement_data = disbursement_data
                    transaction.is_disbursement_enabled = True
                    transaction.save()
            except Exception as e:
                logger.error(f"Error setting up automatic disbursement: {str(e)}")
                # Continue without disbursement if there's an error
        # ============================================================
        
        # If admin, redirect to disbursement setup
        if request.user.is_staff:
            return redirect('ssl_commerz:admin_disbursement_setup', tran_id=tran_id)
        
        # Regular student flow (with or without disbursement)
        parent_profile = student_profile.parent_id.parent_profile if student_profile.parent_id else None
        parent_phone = "N/A"
        if parent_profile and parent_profile.g_mobile_no:
            parent_phone = parent_profile.g_mobile_no
        elif student_profile.student_field.phone_number:  
            parent_phone = student_profile.student_field.phone_number 

        if payment_method == 'trustbank':
            return handle_trust_payment(request, transaction, total_amount, parent_phone, user)
        else:
            # Check if disbursement is enabled for this transaction
            if transaction.is_disbursement_enabled and transaction.disbursement_data:
                return handle_sslcommerz_payment_with_disbursement(request, transaction, total_amount, 
                                                                   student_profile, parent_phone)
            else:
                return handle_sslcommerz_payment_without_disbursement(request, transaction, total_amount, 
                                                                      student_profile, parent_phone)
    
    # Check if Trust Bank is active
    trust_config = TrustBank.objects.first()
    trust_active = trust_config.is_active if trust_config else False
    
    return render(request, 'ssl_commerz/payment.html', {
        'total_amount': total_amount,
        'unpaid_fees': unpaid_fees,
        'trust_active': trust_active
    })



# ====================
# PAYMENT HANDLERS
# ====================

def handle_sslcommerz_payment_without_disbursement(request, transaction, total_amount, student_profile, parent_phone):
    """Handle regular SSLCommerz payment without disbursement"""
    return process_sslcommerz_payment(request, transaction, total_amount, student_profile, parent_phone, 
                                      disbursement_data=None)


def handle_sslcommerz_payment_with_disbursement(request, transaction, total_amount, student_profile, parent_phone):
    """Handle SSLCommerz payment with disbursement"""
    if not transaction.disbursement_data:
        return process_sslcommerz_payment(request, transaction, total_amount, student_profile, parent_phone, 
                                          disbursement_data=None)
    
    # Prepare disbursement data for SSLCommerz with proper formatting
    disbursement_list = []
    for item in transaction.disbursement_data:
        try:
            # Get amount and ensure it's properly formatted
            amount = Decimal(item.get('raw_amount', item.get('amount', '0')))
            formatted_amount = f"{amount:.2f}"
            
            disbursement_list.append({
                "sslcz_ref_id": item['sslcz_ref_id'],
                "amount": formatted_amount
            })
        except (KeyError, ValueError, Decimal.InvalidOperation) as e:
            logger.error(f"Error processing disbursement item: {e}")
            continue
    
    return process_sslcommerz_payment(request, transaction, total_amount, student_profile, parent_phone, 
                                      disbursement_data=disbursement_list)


def process_sslcommerz_payment(request, transaction, total_amount, student_profile, parent_phone, 
                               disbursement_data=None):
    """Common function to process SSLCommerz payment with or without disbursement"""
    ssl_config = SSLC.objects.first()
    if not ssl_config:
        return render(request, 'ssl_commerz/error.html', {'error': 'Payment gateway configuration not found.'})

    sslcz = SSLCOMMERZ({
        'store_id': ssl_config.store_id,
        'store_pass': ssl_config.store_pass,
        'issandbox': (ssl_config.store_penv == 'sandbox')
    })

    # Build address information
    parent_address = "N/A"
    if student_profile:
        address_parts = [
            student_profile.village,
            student_profile.post_office,
            student_profile.ps_or_upazilla,
            student_profile.district
        ]
        parent_address = ", ".join(filter(None, address_parts))  

    post_body = {
        'total_amount': str(total_amount),
        'currency': "BDT",
        'tran_id': transaction.tran_id,
        'success_url': 'https://' + request.get_host() + reverse('ssl_commerz:ssl_success'),
        'fail_url': 'https://' + request.get_host() + reverse('ssl_commerz:ssl_fail'),
        'cancel_url': 'https://' + request.get_host() + reverse('ssl_commerz:ssl_cancel'),
        'ipn_url': 'https://' + request.get_host() + reverse('ssl_commerz:ipn_listener'),
        'emi_option': "0",
        'cus_name': request.user.get_full_name() or "Customer",
        'cus_email': request.user.email or "example@email.com",
        'cus_phone': parent_phone,
        'cus_add1': parent_address[:250],  
        'cus_city': "Dhaka",
        'cus_country': "Bangladesh",
        'shipping_method': "NO",
        'product_name': "Student Fee",
        'product_category': "Fees",
        'product_profile': "general",
        'student_id': student_profile.student_field.id,
        'student_roll': student_profile.roll_no
    }
    
    # Add disbursement data if provided (CORRECTED PARAMETER NAME)
    if disbursement_data:
        # Validate disbursement amounts sum equals total amount
        disbursement_total = Decimal('0.00')
        for item in disbursement_data:
            try:
                disbursement_total += Decimal(item['amount'])
            except (ValueError, KeyError):
                logger.error(f"Invalid amount in disbursement data: {item}")
                return render(request, 'ssl_commerz/error.html', 
                            {'error': 'Invalid disbursement amount format'})
        
        # Round to 2 decimal places for comparison
        disbursement_total = disbursement_total.quantize(Decimal('0.01'))
        total_amount_decimal = Decimal(str(total_amount)).quantize(Decimal('0.01'))
        
        if disbursement_total != total_amount_decimal:
            logger.error(f"Disbursement total mismatch: {disbursement_total} != {total_amount_decimal}")
            return render(request, 'ssl_commerz/error.html', 
                        {'error': f'Disbursement total ({disbursement_total}) does not match transaction amount ({total_amount_decimal})'})
        
        # Add SSLCommerz disbursement parameters
        post_body['disbursement_mode'] = 'MULTIPLE'
        post_body['disbursements_account'] = json.dumps(disbursement_data)
    
    try:
        response = sslcz.createSession(post_body)
    except Exception as e:
        logger.error(f"SSLCommerz API Error: {str(e)}")
        return render(request, 'ssl_commerz/error.html', {'error': 'Payment gateway connection failed.'})

    if not response or not isinstance(response, dict):
        logger.error(f"Invalid SSLCommerz response: {response}")
        return render(request, 'ssl_commerz/error.html', {'error': 'Invalid payment gateway response.'})

    if response.get('status') == 'SUCCESS':
        if ssl_config.store_penv == 'sandbox':
            gateway_url = f"https://sandbox.sslcommerz.com/gwprocess/v4/gw.php?Q=pay&SESSIONKEY={response['sessionkey']}"
        else:
            gateway_url = response['GatewayPageURL']
        
        return redirect(gateway_url)
    else:
        error_msg = response.get('failedreason', 'Payment initiation failed. Please try again.')
        return render(request, 'ssl_commerz/error.html', {'error': error_msg})

def handle_trust_payment(request, transaction, amount, parent_phone, user):
    trust_config = TrustBank.objects.first()
    if not trust_config:
        return render(request, 'ssl_commerz/error.html', {'error': 'Trust Bank configuration missing'})

    data = {
        'MerchantKey': trust_config.merchant_key,
        'MerchantPassword': trust_config.merchant_password,
        'ProductPrice': str(amount),
        'RefId': transaction.tran_id,
        'MerchantName': trust_config.merchant_name,
        'AdditionalInfo': json.dumps({
            'mobile': parent_phone,
            'name': user.get_full_name() or user.username,
        })
    }

    try:
        response = requests.post(
            f"{trust_config.base_url}/initiatePay",
            data=data
        )
        response.raise_for_status()
        response_data = response.json()
        
        if response_data.get('APIstatus') == 'success':
            redirect_url = f"{trust_config.base_url}/customerLoginInterface?SessionId={response_data['SessionId']}"
            return redirect(redirect_url)
        else:
            transaction.status = 'FAILED'
            transaction.save()
            return render(request, 'ssl_commerz/error.html', {'error': 'Trust Bank payment initiation failed'})
            
    except Exception as e:
        transaction.status = 'FAILED'
        transaction.save()
        return render(request, 'ssl_commerz/error.html', {'error': f'Trust Bank connection error: {str(e)}'})


# ====================
# DISBURSEMENT SETUP (ADMIN)
# ====================

@login_required
@staff_member_required
def admin_disbursement_setup(request, tran_id):
    """Admin interface to set up disbursement for a payment"""
    transaction = get_object_or_404(PaymentTransaction, tran_id=tran_id)
    
    # Get all active bank accounts from SSLCommerz
    bank_accounts = BankDisbursementAccount.objects.filter(is_active=True)
    
    if not bank_accounts.exists():
        return render(request, 'ssl_commerz/error.html', {
            'error': 'No bank accounts configured. Please add bank accounts with SSLCommerz reference IDs first.'
        })
    
    # Get unpaid fees for the student
    student_profile = transaction.student_profile
    unpaid_fees = Fees.objects.filter(student_id=student_profile).exclude(status='paid')
    
    # Group fees by fee head
    fee_head_groups = {}
    for fee in unpaid_fees:
        if fee.feetype_id and fee.feetype_id.fees_type:
            fee_head = fee.feetype_id.fees_type.fee_head
            amount = fee.total_fee_after_partial_payments()
            
            if fee_head.id not in fee_head_groups:
                fee_head_groups[fee_head.id] = {
                    'id': fee_head.id,
                    'name': fee_head.name,
                    'total_amount': amount,
                    'fees': [fee]
                }
            else:
                fee_head_groups[fee_head.id]['total_amount'] += amount
                fee_head_groups[fee_head.id]['fees'].append(fee)
    
    fee_heads = list(fee_head_groups.values())
    
    if request.method == 'POST':
        # Step 1: Get number of banks
        num_banks = int(request.POST.get('num_banks', 1))
        
        if num_banks < 1 or num_banks > 4:
            return render(request, 'ssl_commerz/error.html', {
                'error': 'Please select 1 to 4 banks'
            })
        
        # Step 2: Get selected banks
        selected_banks = {}
        for i in range(1, num_banks + 1):
            bank_id = request.POST.get(f'bank_{i}')
            if bank_id:
                try:
                    bank = BankDisbursementAccount.objects.get(id=bank_id, is_active=True)
                    selected_banks[i] = bank
                except BankDisbursementAccount.DoesNotExist:
                    return render(request, 'ssl_commerz/error.html', {
                        'error': f'Invalid bank selected for Bank {i}'
                    })
        
        if len(selected_banks) != num_banks:
            return render(request, 'ssl_commerz/error.html', {
                'error': 'Please select all bank accounts'
            })
        
        # Step 3: Get fee head assignments
        fee_head_assignments = {}
        all_assigned_fee_head_ids = set()
        
        # For first N-1 banks, admin selects fee heads
        for i in range(1, num_banks):
            if i in selected_banks:
                fee_head_ids = request.POST.getlist(f'bank_{i}_fee_heads')
                if fee_head_ids:
                    fee_head_assignments[selected_banks[i].id] = {
                        'bank': selected_banks[i],
                        'fee_head_ids': fee_head_ids
                    }
                    all_assigned_fee_head_ids.update(fee_head_ids)
        
        # Last bank gets remaining fee heads
        last_bank_number = num_banks
        if last_bank_number in selected_banks:
            last_bank = selected_banks[last_bank_number]
            remaining_fee_head_ids = []
            
            for fee_head in fee_heads:
                if str(fee_head['id']) not in all_assigned_fee_head_ids:
                    remaining_fee_head_ids.append(str(fee_head['id']))
            
            if remaining_fee_head_ids:
                fee_head_assignments[last_bank.id] = {
                    'bank': last_bank,
                    'fee_head_ids': remaining_fee_head_ids
                }
            else:
                return render(request, 'ssl_commerz/error.html', {
                    'error': 'No fee heads remaining for the last bank. Please distribute fee heads properly.'
                })
        
        # Step 4: Calculate amounts and prepare disbursement data
        disbursement_data = []
        total_distributed = Decimal('0.00')
        
        for bank_id, assignment in fee_head_assignments.items():
            bank = assignment['bank']
            amount_for_bank = Decimal('0.00')
            assigned_fee_head_names = []
            
            for fee_head in fee_heads:
                if str(fee_head['id']) in assignment['fee_head_ids']:
                    amount_for_bank += fee_head['total_amount']
                    assigned_fee_head_names.append(fee_head['name'])
            
            if amount_for_bank > 0:
                disbursement_data.append({
                    'bank_account_id': bank.id,
                    'bank_display_name': bank.display_name,
                    'bank_name': bank.get_bank_name_display(),
                    'sslcz_ref_id': bank.sslcz_ref_id,
                    'fee_head_ids': assignment['fee_head_ids'],
                    'fee_head_names': assigned_fee_head_names,
                    'amount': f"{amount_for_bank:.2f}", 
                    'raw_amount': float(amount_for_bank) 
                })
                total_distributed += amount_for_bank
        
        # Validate total
        if total_distributed != transaction.amount:
            return render(request, 'ssl_commerz/error.html', {
                'error': f'Distribution error: Total ({total_distributed}) ≠ Transaction ({transaction.amount})'
            })
        
        # Save to transaction
        transaction.disbursement_data = disbursement_data
        transaction.is_disbursement_enabled = True
        transaction.save()
        
        return redirect('ssl_commerz:review_disbursement', tran_id=tran_id)
    
    context = {
        'transaction': transaction,
        'fee_heads': fee_heads,
        'bank_accounts': bank_accounts,
        'total_fee_heads': len(fee_heads)
    }
    
    return render(request, 'ssl_commerz/admin_disbursement_setup.html', context)

def validate_disbursement_data(disbursement_data, total_amount):
    """Validate disbursement data matches SSLCommerz requirements"""
    if not disbursement_data:
        return True, "No disbursement data"
    
    total_disbursement = Decimal('0.00')
    
    for item in disbursement_data:
        # Check required fields
        if 'sslcz_ref_id' not in item:
            return False, f"Missing sslcz_ref_id in item: {item}"
        
        if 'amount' not in item:
            return False, f"Missing amount in item: {item}"
        
        # Validate amount
        try:
            amount = Decimal(str(item['amount']))
            total_disbursement += amount
        except (ValueError, Decimal.InvalidOperation):
            return False, f"Invalid amount format: {item['amount']}"
    
    # Compare with tolerance for floating point arithmetic
    tolerance = Decimal('0.01')
    if abs(total_disbursement - Decimal(str(total_amount))) > tolerance:
        return False, f"Total disbursement ({total_disbursement}) does not match transaction amount ({total_amount})"
    
    return True, "Validation passed"

@login_required
@staff_member_required
def review_disbursement(request, tran_id):
    """Review disbursement configuration before payment"""
    transaction = get_object_or_404(PaymentTransaction, tran_id=tran_id)
    
    if not transaction.disbursement_data:
        return redirect('ssl_commerz:admin_disbursement_setup', tran_id=tran_id)
    
    # Get fee heads for display
    student_profile = transaction.student_profile
    unpaid_fees = Fees.objects.filter(student_id=student_profile).exclude(status='paid')
    
    fee_head_data = {}
    for fee in unpaid_fees:
        if fee.feetype_id and fee.feetype_id.fees_type:
            fee_head = fee.feetype_id.fees_type.fee_head
            if fee_head.id not in fee_head_data:
                fee_head_data[fee_head.id] = {
                    'id': fee_head.id,
                    'name': fee_head.name
                }
    
    fee_heads = list(fee_head_data.values())
    
    # Generate JSON for display
    disbursement_json = []
    if transaction.disbursement_data:
        for item in transaction.disbursement_data:
            disbursement_json.append({
                "sslcz_ref_id": item['sslcz_ref_id'],
                "amount": item['amount']
            })
    
    context = {
        'transaction': transaction,
        'fee_heads': fee_heads,
        'disbursement_data_json': json.dumps(disbursement_json, indent=2)
    }
    
    return render(request, 'ssl_commerz/review_disbursement.html', context)

@login_required
@staff_member_required
def process_disbursement_payment(request, tran_id):
    """Process payment with disbursement configuration"""
    transaction = get_object_or_404(PaymentTransaction, tran_id=tran_id)
    
    if not transaction.is_disbursement_enabled or not transaction.disbursement_data:
        return redirect('ssl_commerz:admin_disbursement_setup', tran_id=tran_id)
    
    # Validate disbursement data
    is_valid, message = validate_disbursement_data(transaction.disbursement_data, transaction.amount)
    if not is_valid:
        return render(request, 'ssl_commerz/error.html', {'error': f'Disbursement validation failed: {message}'})
    
    # Get parent contact information
    student_profile = transaction.student_profile
    parent_profile = student_profile.parent_id.parent_profile if student_profile.parent_id else None
    parent_phone = "N/A"
    if parent_profile and parent_profile.g_mobile_no:
        parent_phone = parent_profile.g_mobile_no
    elif student_profile.student_field.phone_number:  
        parent_phone = student_profile.student_field.phone_number
    
    return handle_sslcommerz_payment_with_disbursement(request, transaction, transaction.amount, 
                                                      student_profile, parent_phone)


# ====================
# SSLCOMMERZ CALLBACKS
# ====================

@csrf_exempt
def ipn_listener(request):
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body.decode('utf-8'))
            else:
                data = request.POST.dict()

            logger.info(f"Received IPN data: {data}")
            
            val_id = data.get('val_id')
            tran_id = data.get('tran_id')
            ssl_status = data.get('status')

            if not all([val_id, tran_id, ssl_status]):
                logger.error("Missing essential parameters in IPN")
                return HttpResponse("Bad Request: Missing parameters", status=400)

            try:
                payment_transaction = PaymentTransaction.objects.get(tran_id=tran_id)
                if payment_transaction.status == 'SUCCESS':
                    logger.info(f"Transaction {tran_id} already processed")
                    return HttpResponse("Already processed", status=200)
                
                if tran_id.startswith("API_"):
                    logger.info(f"Processing mobile transaction {tran_id}")
                    process_successful_transaction(tran_id, val_id, None)
                else:
                    logger.info(f"Processing web transaction {tran_id}")
                    process_successful_transaction(tran_id, val_id, None)

            except PaymentTransaction.DoesNotExist:
                logger.error(f"Transaction {tran_id} not found in database")
                return HttpResponse("Transaction not found", status=404)

            ssl_config = SSLC.objects.first()
            if not ssl_config:
                logger.error("Payment gateway configuration not found in SSLC model")
                return HttpResponse("Server Error: Configuration not found", status=500)

            sslcz = SSLCOMMERZ({
                'store_id': ssl_config.store_id,
                'store_pass': ssl_config.store_pass,
                'issandbox': (ssl_config.store_penv == 'sandbox')
            })

            try: 
                validation_response = sslcz.transaction_validator(val_id)
                logger.info(f"SSLCommerz validation response: {validation_response}")

                if validation_response.get('status') != 'VALID':
                    logger.error(f"Invalid transaction validation for {tran_id}")
                    payment_transaction.status = 'FAILED'
                    payment_transaction.save()
                    return HttpResponse("Invalid transaction validation", status=400)

                with transaction.atomic():
                    payment_transaction.status = 'SUCCESS'
                    payment_transaction.val_id = val_id
                    payment_transaction.bank_tran_id = validation_response.get('bank_tran_id')
                    payment_transaction.card_type = validation_response.get('card_type')
                    payment_transaction.card_no = validation_response.get('card_no')
                    payment_transaction.save()

                    process_successful_transaction(tran_id, val_id, validation_response)

                logger.info(f"Successfully processed transaction {tran_id}")
                return HttpResponse("OK", status=200)

            except Exception as e:
                logger.critical(f"IPN processing failed: {str(e)}", exc_info=True)
                payment_transaction.status = 'FAILED'
                payment_transaction.save()
                return HttpResponse("Server Error", status=500)

        except json.JSONDecodeError:
            logger.error("Invalid JSON received in IPN")
            return HttpResponse("Bad Request: Invalid JSON", status=400)

    return HttpResponse("Method Not Allowed", status=405)


def process_successful_transaction(tran_id, val_id, gateway_data):
    logger.info(f"Processing transaction: {tran_id}")
    try:
        with transaction.atomic():
            payment_transaction = PaymentTransaction.objects.get(tran_id=tran_id)
            
            if payment_transaction.status == 'SUCCESS' and payment_transaction.accounting_completed:
                logger.info(f"Transaction {tran_id} already fully processed.")
                return True

            if payment_transaction.status != 'SUCCESS':
                payment_transaction.status = 'SUCCESS'
                payment_transaction.save(update_fields=['status'])

            student_profile = payment_transaction.student_profile
            if not student_profile:
                logger.error(f"Student profile is None for transaction {tran_id}.")
                raise ValueError(f"Student profile not found for transaction {tran_id}")

            unpaid_fees = Fees.objects.filter(student_id=student_profile).exclude(status='paid')
            if not unpaid_fees.exists():
                logger.warning(f"No unpaid fees for student profile {student_profile}.")
                return False

            logger.info(f"Found {unpaid_fees.count()} unpaid fees for {student_profile}.")
            
            for fee in unpaid_fees:
                remaining = fee.total_fee() - fee.total_paid_amount()
                if remaining > 0:
                    logger.info(f"Processing fee {fee.id}, remaining amount: {remaining}")

                    PartialPayment.objects.create(fee=fee, amount=remaining, created_by=payment_transaction.user)
                    fee.update_fee_status()
                    fee.save()

                    income_category, _ = LedgerCategory.objects.get_or_create(name='Income', defaults={'description': 'Income category'})
                    tuition_ledger, _ = Ledger.objects.get_or_create(
                        name='Tuition Fees Income',
                        defaults={'category': income_category, 'code': 'TFI001', 'balance_type': 'Credit'}
                    )
                    cash_ledger = Ledger.objects.get(name='Cash in Hand', category__name='Asset')

                    unique_voucher_no = f"RECV-{tran_id}-{fee.id}"

                    Receive.objects.create(
                        voucher_no=unique_voucher_no,
                        date=timezone.now().date(),
                        amount=remaining,  
                        student=student_profile,
                        fee_head=FeeHead.objects.get_or_create(name='Tuition Fees')[0],
                        cash_ledger=cash_ledger,
                        income_ledger=tuition_ledger,
                        description=f"Payment via {payment_transaction.get_gateway_display()} ({tran_id})",
                    )

            payment_transaction.accounting_completed = True
            payment_transaction.save(update_fields=['accounting_completed'])

            logger.info(f"Successfully processed transaction {tran_id}.")
            return True
            
    except Exception as e:
        logger.error(f"Payment processing failed for {tran_id}: {str(e)}", exc_info=True)
        return False


@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        tran_id = request.POST.get('tran_id')
    else:
        tran_id = request.GET.get('tran_id')

    if not tran_id:
        return render(request, 'ssl_commerz/error.html', {'error': 'Transaction ID not provided'})

    try:
        transaction = PaymentTransaction.objects.get(tran_id=tran_id)
        
        if transaction.status == 'SUCCESS':
            if not transaction.receipt_pdf:
                pdf_response = payment_receipt(request, tran_id)
                from django.core.files.base import ContentFile
                file_name = f"receipts/{tran_id}.pdf"
                transaction.receipt_pdf.save(file_name, ContentFile(pdf_response.content))
            
            response = render(request, 'ssl_commerz/success.html', {'transaction': transaction})
            response['Content-Disposition'] = f'attachment; filename="receipt_{tran_id}.pdf"'
            return response

        try:
            ssl_config = SSLC.objects.first()
            if not ssl_config:
                logger.error("Payment gateway configuration not found in SSLC model")
                return render(request, 'ssl_commerz/error.html', {'error': 'Payment gateway configuration not found'})

            sslcz = SSLCOMMERZ({
                'store_id': ssl_config.store_id,
                'store_pass': ssl_config.store_pass,
                'issandbox': (ssl_config.store_penv == 'sandbox')
            })

            tran_response = sslcz.transaction_query_tranid(tran_id)
            logger.info(f"Transaction response: {tran_response}")

            elements = tran_response.get('element', [])
            if not elements:
                logger.error(f"No transaction details found for {tran_id}")
                transaction.status = 'FAILED'
                transaction.save()
                return render(request, 'ssl_commerz/error.html', {'error': 'Transaction not found'})

            element = elements[0]
            if element.get('status') != 'VALID':
                logger.error(f"Transaction {tran_id} failed with status: {element.get('status')}")
                transaction.status = 'FAILED'
                transaction.save()
                return render(request, 'ssl_commerz/error.html', {'error': 'Payment validation failed'})

            transaction.status = 'SUCCESS'
            transaction.val_id = element.get('val_id')
            transaction.bank_tran_id = element.get('bank_tran_id')
            transaction.card_type = element.get('card_type')
            transaction.card_no = element.get('card_no')
            transaction.save()

            success = process_successful_transaction(
                tran_id, 
                element.get('val_id'), 
                element 
            )

            # Generate and save PDF
            pdf_response = payment_receipt(request, tran_id)
            from django.core.files.base import ContentFile
            file_name = f"receipts/{tran_id}.pdf"
            transaction.receipt_pdf.save(file_name, ContentFile(pdf_response.content))
            transaction.save()

            # Create response with PDF download
            response = render(request, 'ssl_commerz/success.html', {'transaction': transaction})
            response['Content-Disposition'] = f'attachment; filename="receipt_{tran_id}.pdf"'
            return response

        except Exception as e:
            logger.error(f"Error processing transaction: {str(e)}", exc_info=True)
            transaction.status = 'FAILED'
            transaction.save()
            return render(request, 'ssl_commerz/error.html', {'error': 'Payment processing failed'})

    except PaymentTransaction.DoesNotExist:
        return render(request, 'ssl_commerz/error.html', {'error': 'Transaction not found'})


def payment_fail(request):
    tran_id = request.GET.get('tran_id')
    transaction = PaymentTransaction.objects.get(tran_id=tran_id)
    return render(request, 'ssl_commerz/fail.html', {'transaction': transaction})


def payment_cancel(request):
    tran_id = request.GET.get('tran_id')
    transaction = PaymentTransaction.objects.get(tran_id=tran_id)
    return render(request, 'ssl_commerz/cancel.html', {'transaction': transaction})


# ====================
# RECEIPT GENERATION
# ====================

from io import BytesIO
from django.core.files.base import ContentFile
from num2words import num2words
from django.template.loader import get_template
from xhtml2pdf import pisa


def payment_receipt(request, tran_id):
    try:
        transaction = get_object_or_404(PaymentTransaction, tran_id=tran_id)
        
        # Check if this is February 2025
        if transaction.tran_date.year == 2025 and transaction.tran_date.month == 2:
            return HttpResponse("PDF downloads are temporarily unavailable for February 2025", status=403)
        
        if transaction.receipt_pdf:
            response = HttpResponse(transaction.receipt_pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="receipt_{tran_id}.pdf"'
            return response
            
        student_profile = transaction.student_profile
        
        # ============================================================
        # UPDATED: Get fee heads from multiple sources
        # ============================================================
        
        fee_heads = {}
        total_paid = Decimal('0.00')
        
        # METHOD 1: Check if disbursement data exists
        if transaction.disbursement_data:
            # Extract fee heads from disbursement data
            for disbursement_item in transaction.disbursement_data:
                fee_head_names = disbursement_item.get('fee_head_names', [])
                amount = Decimal(disbursement_item.get('amount', '0.00'))
                
                if fee_head_names:
                    for fee_head_name in fee_head_names:
                        if fee_head_name not in fee_heads:
                            fee_heads[fee_head_name] = Decimal('0.00')
                        # Distribute amount equally among fee heads for this disbursement
                        fee_heads[fee_head_name] += amount / len(fee_head_names)
                else:
                    # If no fee head names, use bank name
                    bank_name = disbursement_item.get('bank_display_name', 'Bank Payment')
                    if bank_name not in fee_heads:
                        fee_heads[bank_name] = Decimal('0.00')
                    fee_heads[bank_name] += amount
                
                total_paid += amount
        
        # METHOD 2: If no disbursement data, check PartialPayment records
        if not fee_heads:
            # Get payments created within 1 minute of the transaction
            time_threshold = transaction.tran_date + timedelta(minutes=1)
            partial_payments = PartialPayment.objects.filter(
                fee__student_id=student_profile,
                payment_date__gte=transaction.tran_date,
                payment_date__lte=time_threshold,
                created_by=transaction.user
            ).select_related('fee__feetype_id')
            
            # For Trust Bank payments, use the transaction amount if no partial payments found
            if transaction.gateway == 'trustbank' and not partial_payments.exists():
                fee_heads["Trust Bank Payment"] = transaction.amount
                total_paid = transaction.amount
            else:
                # Regular processing for other payment methods
                for payment in partial_payments:
                    fee_type = payment.fee.feetype_id.fees_title if payment.fee.feetype_id else "Miscellaneous"
                    fee_heads[fee_type] = fee_heads.get(fee_type, Decimal('0.00')) + payment.amount
                    total_paid += payment.amount
        
        # METHOD 3: If still no fee heads, fall back to transaction amount
        if not fee_heads:
            fee_heads["Payment"] = transaction.amount
            total_paid = transaction.amount
        
        # ============================================================
        # Prepare context with safe defaults
        # ============================================================
        
        # Get student details with safe defaults
        class_info = "N/A"
        section_info = "N/A"
        group_info = "N/A"
        shift_info = "N/A"
        
        if student_profile.class_id:
            class_info = student_profile.class_id.class_group_id.class_id.name if student_profile.class_id.class_group_id and student_profile.class_id.class_group_id.class_id else "N/A"
            section_info = student_profile.class_id.section_id.name if student_profile.class_id.section_id else "N/A"
            group_info = student_profile.class_id.class_group_id.group_id.name if student_profile.class_id.class_group_id and student_profile.class_id.class_group_id.group_id else "N/A"
            shift_info = student_profile.class_id.shift_id.name if student_profile.class_id.shift_id else "N/A"
        
        context = {
            'name': student_profile.student_field.name if student_profile.student_field else "N/A",
            'student_id': str(student_profile.roll_no) if student_profile.roll_no else "N/A", 
            'shift': shift_info,
            'version': student_profile.get_version_display() if hasattr(student_profile, 'get_version_display') else "N/A",
            'payment_time': transaction.tran_date.strftime("%Y-%m-%d %H:%M:%S"),
            'transaction_id': tran_id,
            'class': class_info,
            'section': section_info,
            'group': group_info,
            'payment_type': transaction.card_type or transaction.get_gateway_display(),
            'fee_heads': [{'name': k, 'amount': v} for k, v in fee_heads.items()],
            'total': total_paid,
            'total_in_words': num2words(total_paid, lang='en').title() + " Taka Only",
        }

        template = get_template('ssl_commerz/payment_receipt.html')
        html = template.render(context)
        
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
        
        if pisa_status.err:
            logger.error(f"PDF creation failed: {pisa_status.err}")
            return HttpResponse("Error generating PDF", status=500)
            
        try:
            pdf_buffer.seek(0)
            transaction.receipt_pdf.save(
                f'receipts/{tran_id}.pdf',
                ContentFile(pdf_buffer.read()),
                save=False
            )
            transaction.save()
        except Exception as e:
            logger.warning(f"PDF save failed: {str(e)} (proceeding with download)")

        pdf_buffer.seek(0)
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{tran_id}.pdf"'
        return response

    except Exception as e:
        logger.error(f"Receipt generation failed: {str(e)}", exc_info=True)
        return HttpResponse("Error generating receipt", status=500)

# ====================
# TRANSACTION HISTORY
# ====================

def transaction_month_list(request):
    months = PaymentTransaction.objects.filter(
        user=request.user, 
        status='SUCCESS'
    ).annotate(
        month=TruncMonth('tran_date')
    ).values('month').annotate(
        total=Count('id')
    ).order_by('-month')
    
    return render(request, 'ssl_commerz/transaction_months.html', {
        'months': months
    })


def transaction_month_detail(request, year, month):
    start_date = make_aware(datetime(year, month, 1))
    end_date = start_date + timedelta(days=31)  # Cover entire month
    
    transactions = PaymentTransaction.objects.filter(
        user=request.user,
        status='SUCCESS',
        tran_date__gte=start_date,
        tran_date__lt=end_date
    ).order_by('-tran_date')
    
    # Add flag for February 2025 to template context
    is_feb_2025 = (year == 2025 and month == 2)
    
    return render(request, 'ssl_commerz/transaction_month_detail.html', {
        'transactions': transactions,
        'month': f"{year}-{month:02d}",
        'is_feb_2025': is_feb_2025
    })


# ====================
# TRUST BANK CALLBACKS
# ====================

def trust_payment_success(request):
    # Get required parameters from query string
    session_id = request.GET.get('SessionId')
    status_param = request.GET.get('Status')
    ref_id = request.GET.get('RefId')

    # Validate presence of required parameters
    if not ref_id:
        return render(request, 'ssl_commerz/error.html', {'error': 'Transaction ID (RefId) not provided'})
    if not session_id:
        return render(request, 'ssl_commerz/error.html', {'error': 'Session ID not provided'})
    if not status_param:
        return render(request, 'ssl_commerz/error.html', {'error': 'Payment status not provided'})

    try:
        # Retrieve transaction with safety checks
        transaction = PaymentTransaction.objects.get(tran_id=ref_id)
    except PaymentTransaction.DoesNotExist:
        return render(request, 'ssl_commerz/error.html', {'error': 'Transaction not found'})

    # Verify Trust Bank configuration
    trust_config = TrustBank.objects.first()
    if not trust_config:
        return render(request, 'ssl_commerz/error.html', {'error': 'Trust Bank configuration missing'})

    try:
        # Validate transaction with Trust Bank API
        val_response = requests.post(
            f"{trust_config.base_url}/getStatus",
            data={
                'MerchantKey': trust_config.merchant_key,
                'MerchantPassword': trust_config.merchant_password,
                'RefId': ref_id,
                'SessionId': session_id
            },
            timeout=10
        )
        val_response.raise_for_status()
        val_data = val_response.json()
        
        # Correct status check for Trust Bank's 'Y' value
        if val_data.get('APIstatus') == 'success' and val_data.get('Status') == 'Y':
            # Update transaction status
            transaction.status = 'SUCCESS'
            transaction.bank_tran_id = val_data.get('BankTransactionID')
            transaction.save()
            
            # Process accounting entries
            try:
                process_successful_transaction(transaction.tran_id, None, None)
            except Exception as process_error:
                logger.error(f"Accounting processing failed: {str(process_error)}")
                return render(request, 'ssl_commerz/error.html', {
                    'error': f'Payment successful but accounting failed: {str(process_error)}'
                })

            # Generate receipt if not exists
            if not transaction.receipt_pdf:
                try:
                    pdf_response = payment_receipt(request, ref_id)
                    transaction.receipt_pdf.save(
                        f"receipts/{ref_id}.pdf",
                        ContentFile(pdf_response.content),
                        save=False
                    )
                    transaction.save()
                except Exception as pdf_error:
                    logger.error(f"Receipt generation failed: {str(pdf_error)}")

            # Render Trust Bank's success template directly
            return render(request, 'ssl_commerz/trust_success.html', {
                'transaction': transaction,
                'bank_transaction_id': transaction.bank_tran_id,
                'amount': transaction.amount
            })
            
        else:
            # Handle failed validation
            transaction.status = 'FAILED'
            transaction.fail_reason = val_data.get('ErrorDesc', 'Payment declined by bank')
            transaction.save()
            logger.warning(f"Trust payment failed: {val_data}")
            return redirect(reverse('ssl_commerz:trust_fail') + f'?RefId={ref_id}')

    except requests.RequestException as req_error:
        # Handle API connection errors
        transaction.status = 'FAILED'
        transaction.fail_reason = f"Connection error: {str(req_error)}"
        transaction.save()
        logger.error(f"Trust API connection failed: {str(req_error)}")
        return render(request, 'ssl_commerz/error.html', {
            'error': f'Could not validate payment: {str(req_error)}'
        })
        
    except Exception as e:
        # Handle generic errors
        transaction.status = 'FAILED'
        transaction.fail_reason = str(e)
        transaction.save()
        logger.error(f"Payment processing failed: {str(e)}", exc_info=True)
        return render(request, 'ssl_commerz/error.html', {
            'error': f'Payment processing failed: {str(e)}'
        })


def trust_payment_fail(request):
    ref_id = request.GET.get('RefId')
    try:
        transaction = PaymentTransaction.objects.get(tran_id=ref_id)
    except PaymentTransaction.DoesNotExist:
        return redirect('ssl_commerz:ssl_fail')
    
    return render(request, 'ssl_commerz/trust_fail.html', {
        'transaction': transaction,
        'error': transaction.fail_reason if transaction.fail_reason else 'Payment failed'
    })


def trust_payment_cancel(request):
    ref_id = request.GET.get('RefId')
    try:
        transaction = PaymentTransaction.objects.get(tran_id=ref_id)
    except PaymentTransaction.DoesNotExist:
        return redirect('ssl_commerz:ssl_cancel')
    
    return render(request, 'ssl_commerz/trust_cancel.html', {
        'transaction': transaction,
        'error': 'Payment cancelled by user'
    })


# ====================
# API ENDPOINTS
# ====================

def get_fee_heads_for_student(request):
    """API endpoint to get fee heads for a student"""
    student_id = request.GET.get('student_id')
    if not student_id:
        return JsonResponse({'error': 'Student ID required'}, status=400)
    
    try:
        student_profile = StudentProfile.objects.get(id=student_id)
        unpaid_fees = Fees.objects.filter(student_id=student_profile).exclude(status='paid')
        
        fee_heads = []
        for fee in unpaid_fees:
            if fee.feetype_id and fee.feetype_id.fees_type:
                fee_head = fee.feetype_id.fees_type.fee_head
                fee_heads.append({
                    'id': fee_head.id,
                    'name': fee_head.name,
                    'amount': str(fee.total_fee_after_partial_payments()),
                    'fee_id': fee.id
                })
        
        # Remove duplicates
        unique_fee_heads = []
        seen_ids = set()
        for fh in fee_heads:
            if fh['id'] not in seen_ids:
                unique_fee_heads.append(fh)
                seen_ids.add(fh['id'])
        
        return JsonResponse({'fee_heads': unique_fee_heads})
    
    except StudentProfile.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    
    
def generate_automatic_disbursement_data(student_profile, total_amount):
    """
    Automatically generate disbursement data for student payments
    based on FeeHeadBankDistribution
    """
    from crucial.models import Fees
    
    unpaid_fees = Fees.objects.filter(student_id=student_profile).exclude(status='paid')
    if not unpaid_fees.exists():
        return None
    
    # Group fees by fee head
    fee_head_amounts = {}
    for fee in unpaid_fees:
        if fee.feetype_id and fee.feetype_id.fees_type:
            fee_head = fee.feetype_id.fees_type.fee_head
            amount = fee.total_fee_after_partial_payments()
            
            if fee_head.id not in fee_head_amounts:
                fee_head_amounts[fee_head.id] = {
                    'fee_head': fee_head,
                    'amount': amount,
                    'fees': [fee]
                }
            else:
                fee_head_amounts[fee_head.id]['amount'] += amount
                fee_head_amounts[fee_head.id]['fees'].append(fee)
    
    # Check if any fee heads have bank distributions
    disbursement_items = {}
    
    for fee_head_id, data in fee_head_amounts.items():
        fee_head = data['fee_head']
        
        # Get bank distributions for this fee head
        distributions = FeeHeadBankDistribution.objects.filter(
            fee_head=fee_head,
            is_active=True
        )
        
        if distributions.exists():
            for distribution in distributions:
                bank_account = distribution.bank_account
                amount = (data['amount'] * distribution.percentage) / 100
                
                if bank_account.id not in disbursement_items:
                    disbursement_items[bank_account.id] = {
                        'bank_account': bank_account,
                        'amount': amount,
                        'fee_heads': [fee_head.name],
                        'fee_head_ids': [str(fee_head.id)]
                    }
                else:
                    disbursement_items[bank_account.id]['amount'] += amount
                    disbursement_items[bank_account.id]['fee_heads'].append(fee_head.name)
                    disbursement_items[bank_account.id]['fee_head_ids'].append(str(fee_head.id))
    
    # Convert to the required format
    if not disbursement_items:
        return None
    
    disbursement_data = []
    total_disbursed = Decimal('0.00')
    
    for bank_id, item in disbursement_items.items():
        bank_account = item['bank_account']
        amount = item['amount']
        
        disbursement_data.append({
            'bank_account_id': bank_account.id,
            'bank_display_name': bank_account.display_name,
            'bank_name': bank_account.get_bank_name_display(),
            'sslcz_ref_id': bank_account.sslcz_ref_id,
            'fee_head_ids': item['fee_head_ids'],
            'fee_head_names': item['fee_heads'],
            'amount': str(amount),
            'raw_amount': float(amount)
        })
        
        total_disbursed += amount
    
    # Validate total disbursed equals total amount (with tolerance for rounding)
    if abs(total_disbursed - total_amount) > Decimal('0.01'):
        logger.warning(f"Disbursement total mismatch: {total_disbursed} != {total_amount}")
        # Adjust the last item to match total amount
        if disbursement_data:
            adjustment = total_amount - total_disbursed
            last_item = disbursement_data[-1]
            last_amount = Decimal(last_item['amount'])
            last_item['amount'] = str(last_amount + adjustment)
            last_item['raw_amount'] = float(last_amount + adjustment)
    
    return disbursement_data