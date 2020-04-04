/*
 * Based on: https://django-haystack.readthedocs.io/en/master/autocomplete.html
 *
 * © Copyright 2009-2016, Daniel Lindsley
 * Licensed under the 3-clause BSD license
 */

var Autocomplete = function (options) {
    this.form_selector = options.form_selector || '.autocomplete';
    this.url = options.url || Urls.searchbarSnippets();
    this.delay = parseInt(options.delay || 300);
    this.minimum_length = parseInt(options.minimum_length || 3);
    this.form_elem = null;
    this.query_box = null;
    this.selected_element = null;
};

Autocomplete.prototype.setup = function () {
    var self = this;

    this.form_elem = $(this.form_selector);
    this.query_box = this.form_elem.find('input[name=q]');


    // Remove search results if input field isn't focused anymore
    $('body').click(function (evt) {
        if ($.inArray(evt.target.id, ["search", "search-results"]) >= 0) {
            return;
        }

        //For descendants of search-results being clicked, remove this check if you do not want to put constraint on descendants.
        let distance = $(evt.target).closest('#search-results').length;
        if (0 < distance && distance <= 2) {
            return;
        }
        //Do processing of click event here for every element except with id search-results
        $('#search-results').remove();

    });
    // Trigger the "keyup" event if input gets focused

    this.query_box.focus(function () {
        self.query_box.trigger("keyup");
    });

    // Watch the input box.
    this.query_box.keydown(function (e) {
        var query = self.query_box.val();

        if (e.which === 38) { // Keypress Up
            if (!self.selected_element) {
                self.setSelectedResult($("#search-collection").children().last());
                return false;
            }

            let prev = self.selected_element.prev();
            if (prev.length > 0) {
                self.setSelectedResult(prev);
            }
            return false;
        }

        if (e.which === 40) { // Keypress Down
            if (!self.selected_element) {
                self.setSelectedResult($("#search-collection").children().first());
                return false;
            }

            let next = self.selected_element.next();
            if (next.length > 0) {
                self.setSelectedResult(next);
            }
            return false;
        }

        if (query.length < self.minimum_length) {
            $("#search-results").remove();
            return true;
        }

        self.fetch(query);
        return true;
    });

    // On selecting a result, remove result box
    this.form_elem.on('click', '#search-results', function (ev) {
        $('#search-results').remove();
        return true;
    });

    // Disable browser's own autocomplete
    // We do this here so users without JavaScript can keep it enabled
    this.query_box.attr('autocomplete', 'off');
};

Autocomplete.prototype.fetch = function (query) {
    var self = this;

    $.ajax({
        url: this.url
        , data: {
            'q': query
        }
        , success: function (data) {
            self.show_results(data);
        }
    })
};

Autocomplete.prototype.show_results = function (data) {
    $('#search-results').remove();
    var results_wrapper = $('<div id="search-results">' + data + '</div>');
    this.query_box.after(results_wrapper);
};

Autocomplete.prototype.setSelectedResult = function (element) {
    if (this.selected_element) {
        this.selected_element.removeClass("active");
    }
    element.addClass("active");
    this.selected_element = element;
    console.log("New element: ", element);
};
