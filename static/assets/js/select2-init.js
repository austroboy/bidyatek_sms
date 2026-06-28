/* =============================================================================
   Global Select2 auto-enhancer  (EduTech UI upgrade)
   Turns every <select> into a searchable, teal-themed Select2 dropdown so the
   option highlight is consistent teal across ALL browsers (not the native blue).

   Design goals / safety:
   - No HTML changes needed.
   - Re-runs after HTMX swaps so modal-loaded selects (Fees/Exam Add-Edit) are
     enhanced too.
   - Skips selects that a page already initialised itself (avoids double-init).
   - When a select lives inside a Bootstrap modal, Select2 is attached with
     `dropdownParent` = that modal, so the dropdown isn't clipped / mis-stacked.
   - Multiple selects get the multiple-friendly config automatically.
   ============================================================================= */
(function () {
  "use strict";

  // Bail out quietly if jQuery or Select2 aren't available.
  function ready() {
    return (typeof window.jQuery !== "undefined") && (typeof window.jQuery.fn !== "undefined") && (typeof window.jQuery.fn.select2 !== "undefined");
  }

  function enhance(root) {
    if (!ready()) return;
    var $ = window.jQuery;
    var scope = root ? $(root) : $(document);

    scope.find("select").each(function () {
      var $sel = $(this);

      // Skip if already a Select2, or explicitly opted out.
      if ($sel.hasClass("select2-hidden-accessible")) return;
      if ($sel.data("no-select2") !== undefined) return;
      if ($sel.attr("data-no-select2") !== undefined) return;
      // Skip tiny framework selects (e.g. DataTables length menu) — they look
      // fine native and enhancing them can fight the plugin. Heuristic: skip
      // selects with a name like *_length or inside a dataTables wrapper.
      if ($sel.attr("name") && /_length$/.test($sel.attr("name"))) return;
      if ($sel.closest(".dataTables_wrapper").length) return;

      var opts = {
        width: "100%",
        theme: "default"
      };

      // If inside a modal, anchor the dropdown to the modal so it isn't clipped.
      var $modal = $sel.closest(".modal");
      if ($modal.length) {
        opts.dropdownParent = $modal;
      }

      // Use a placeholder if the first option is an empty/dashes placeholder.
      var first = $sel.find("option").first();
      if (first.length && (first.val() === "" || /^-+$/.test($.trim(first.text())))) {
        opts.placeholder = first.text();
        opts.allowClear = !$sel.prop("multiple");
      }

      try {
        $sel.select2(opts);
      } catch (e) {
        /* never let a single bad select break the page */
        if (window.console) console.warn("select2 init skipped for a select:", e);
      }
    });
  }

  function init() {
    // Defer to end of the event loop so any page-specific inline Select2
    // initialisation (which may add custom options like AJAX/templates) runs
    // FIRST and wins; our skip-if-already-enhanced check then leaves it alone.
    setTimeout(function () { enhance(document); }, 0);
  }

  // Initial run on DOM ready.
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Re-enhance content swapped in by HTMX (e.g. Add-Edit modals).
  document.body && document.body.addEventListener("htmx:afterSwap", function (evt) {
    var target = (evt && evt.detail && evt.detail.target) ? evt.detail.target : document;
    // small timeout so the modal is in the DOM & visible before we attach
    setTimeout(function () { enhance(target); }, 30);
  });

  // Also catch Bootstrap modals shown without HTMX.
  document.body && document.body.addEventListener("shown.bs.modal", function (evt) {
    enhance(evt.target);
  });
})();