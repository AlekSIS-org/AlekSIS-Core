function initDatePicker(sel) {
    // Initialize datepicker [MAT]
    const format = get_format('SHORT_DATE_FORMAT').toLowerCase().replace('d', 'dd').replace('m', 'mm').replace('y', 'yyyy');
    const el = $(sel).datepicker({
        format: format,
        // Pull translations from Django helpers
        i18n: {
            months: calendarweek_i18n.month_names,
            monthsShort: calendarweek_i18n.month_abbrs,
            weekdays: calendarweek_i18n.day_names,
            weekdaysShort: calendarweek_i18n.day_abbrs,
            weekdaysAbbrev: calendarweek_i18n.day_abbrs.map(([v]) => v),

            // Buttons
            today: gettext('Today'),
            cancel: gettext('Cancel'),
            done: gettext('OK'),
        },

        // Set monday as first day of week
        firstDay: get_format('FIRST_DAY_OF_WEEK'),
        autoClose: true
    });
    el.datepicker("setDate", $(sel).val());
    return el;
}

function initTimePicker(sel) {
    // Initialize timepicker [MAT]
    return $(sel).timepicker({
        twelveHour: false,
        autoClose: true,
        i18n: {
            cancel: 'Abbrechen',
            clear: 'Löschen',
            done: 'OK'
        },
    });
}

$(document).ready(function () {
    $("dmc-datetime input").addClass("datepicker");
    $("[data-form-control='date']").addClass("datepicker");
    $("[data-form-control='time']").addClass("timepicker");

    // Initialize sidenav [MAT]
    $(".sidenav").sidenav();

    // Initialize datepicker [MAT]
    initDatePicker(".datepicker");

    // Initialize timepicker [MAT]
    initTimePicker(".timepicker");

    // Initialize tooltip [MAT]
    $('.tooltipped').tooltip();

    // Initialize select [MAT]
    $('select').formSelect();

    // Initialize dropdown [MAT]
    $('.dropdown-trigger').dropdown();

    // If JS is activated, the language form will be auto-submitted
    $('.language-field select').change(function () {

        // Ugly bug fix to ensure correct value
        const selectEl = $("select[name=language]");
        selectEl.val(selectEl.val());

        $(".language-form").submit();
    });

    // If auto-submit is activated (see above), the language submit must not be visible
    $(".language-submit-p").hide();

    // Initalize print button
    $("#print").click(function () {
        window.print();
    });

    // Initialize Collapsible [MAT]
    $('.collapsible').collapsible();

    // Initialize FABs [MAT]
    $('.fixed-action-btn').floatingActionButton();

    // Initialize Modals [MAT]
    $('.modal').modal();

    // Intialize Tabs [Materialize]
    $('.tabs').tabs();

    // Sync color picker
    $(".jscolor").change(function () {
        $("#" + $(this).data("preview")).css("color", $(this).val());
    });

    $('table.datatable').each(function (index) {
        $(this).DataTable({
            "paging": false
        });
    });

    // Initialise auto-completion for search bar
    window.autocomplete = new Autocomplete({minimum_length: 2});
    window.autocomplete.setup();

    // Initialize text collapsibles [MAT, own work]
    $(".text-collapsible").addClass("closed").removeClass("opened");

    $(".text-collapsible .open-icon").click(function (e) {
        var el = $(e.target).parent();
        el.addClass("opened").removeClass("closed");
    });
    $(".text-collapsible .close-icon").click(function (e) {
        var el = $(e.target).parent();
        el.addClass("closed").removeClass("opened");
    });
});

// Show notice if serviceworker broadcasts that the current page comes from its cache
const channel = new BroadcastChannel("cache-or-not");
channel.addEventListener("message", event => {
    if ((event.data) && !($("#cache-alert").length)) {
        $("main").prepend('<div id="cache-alert" class="alert warning"><p><i class="material-icons left">warning</i>' + gettext("This page may contain outdated information since there is no internet connection.") + '</p> </div>')
    }
});
