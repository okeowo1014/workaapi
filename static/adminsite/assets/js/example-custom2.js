"use strict";

(function (NioApp, $) {
  'use strict';

  // var dualListbox = new DualListbox('#basic-listbox');
  // var preselectedListbox = new DualListbox('#preselected-listbox');
  // var nosearchListbox = new DualListbox('#nosearch-listbox');
  // nosearchListbox.search.classList.add('dual-listbox__search--hidden');

  var customLabelsList = new DualListbox('#custom-labels-list', {
    availableTitle: 'Applicants',
    selectedTitle: 'Employed',
    // addButtonText: '<em class="icon ni ni-chevron-right"></em>',
    // removeButtonText: '<em class="icon ni ni-chevron-left"></em>',
    // addAllButtonText: '<em class="icon ni ni-chevrons-right"></em>',
    // removeAllButtonText: '<em class="icon ni ni-chevrons-left"></em>'
  });
  customLabelsList.search.classList.add('dual-listbox__search--hidden');

})(NioApp, jQuery);