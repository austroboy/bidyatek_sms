/**
 * Perfect Scrollbar
 */
'use strict';

document.addEventListener('DOMContentLoaded', function () {
  (function () {
    const fees = document.getElementById('fees'),
      expense = document.getElementById('expense')

      const horizontalformset = document.getElementById('horizontalformset')

      
    // Vertical Example
    // --------------------------------------------------------------------
    if (fees) {
      new PerfectScrollbar(fees, {
        wheelPropagation: false
      });
    }
    if (expense) {
      new PerfectScrollbar(expense, {
        wheelPropagation: false
      });
    }

    // Horizontal Example
    // --------------------------------------------------------------------
    if (horizontalformset) {
      new PerfectScrollbar(horizontalformset, {
        wheelPropagation: true,
        suppressScrollY: true
      });
    }

    
  })();
});
