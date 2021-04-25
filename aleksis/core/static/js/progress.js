const OPTIONS = getJSONScript("progress_options");

const STYLE_CLASSES = {
    10: 'info',
    20: 'info',
    25: 'success',
    30: 'warning',
    40: 'error',
};

const ICONS = {
    10: 'info',
    20: 'info',
    25: 'check_circle',
    30: 'warning',
    40: 'error',
};

function setProgress(progress) {
    $("#progress-bar").css("width", progress + "%");
}

function renderMessageBox(level, text) {
    return '<div class="alert ' + STYLE_CLASSES[level] + '"><p><i class="material-icons left">' + ICONS[level] + '</i>' + text + '</p></div>';
}

function customProgress(progressBarElement, progressBarMessageElement, progress) {
    setProgress(progress.percent);

    if (progress.hasOwnProperty("messages")) {
        const messagesBox = $("#messages");

        // Clear container
        messagesBox.html("")

        // Render message boxes
        $.each(progress.messages, function (i, message) {
            messagesBox.append(renderMessageBox(message[0], message[1]));
        })
    }
}


function customSuccess(progressBarElement, progressBarMessageElement) {
    setProgress(100);
    $("#result-alert").addClass("success");
    $("#result-icon").text("check_circle");
    $("#result-text").text(OPTIONS.success);
    $("#result-box").show();
    const redirect = "redirect_on_success" in OPTIONS;
    if (redirect) {
        window.location.replace(OPTIONS.redirect_on_success);
    }
}

function customError(progressBarElement, progressBarMessageElement) {
    setProgress(100);
    $("#result-alert").addClass("error");
    $("#result-icon").text("error");
    $("#result-text").text(OPTIONS.error);
    $("#result-box").show();
}

$(document).ready(function () {
    $("#progress-bar").removeClass("indeterminate").addClass("determinate");

    var progressUrl = Urls["celeryProgress:taskStatus"](OPTIONS.task_id);
    CeleryProgressBar.initProgressBar(progressUrl, {
        onProgress: customProgress,
        onSuccess: customSuccess,
        onError: customError,
    });
});
