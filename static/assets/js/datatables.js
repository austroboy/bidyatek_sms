"use strict";

$(document).ready(function () {
  const dtSelector = "#datatable";
  const dt = $(dtSelector).DataTable({
    fixedHeader: { header: true },
    //   dom: "<'row'<'col-sm-4'B><'col-sm-8'f>>" + "<'row'<'col-sm-12'tr>>" + "<'row'<'col-sm-5'i><'col-sm-7'p>>",
    dom: `<'row'<'col-sm-12 col-md-6'B><'col-sm-12 col-md-6 d-flex justify-content-end'fl>>
            <'row dt-row'<'col-sm-12'tr>>
            <'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>`,
    
    buttons: {

    buttons: [
        {
            
            text: "Add new record",
            attr: {
                role: "button",
                class: "btn btn-primary btn-create"
            },
            action: function (datatable) {
                /** @todo Add action code */
                alert("Add new record!");
            }
        },

        {
            extend: "collection",
            text: "Export",
            autoClose: true,
            buttons: ["csvHtml5", "pdfHtml5"]
        },

    ]
},
    pagingType: "simple_numbers",
    pageLength: 25,
    responsive: true
  });
});
