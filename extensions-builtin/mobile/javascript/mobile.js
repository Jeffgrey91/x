var isSetupForMobile = false;

function isMobile() {
    for (var tab of ["txt2img", "img2img"]) {
        var imageTab = gradApp().getElementById(tab + '_results');
        if (imageTab && imageTab.offsetParent && imageTab.offsetLeft == 0) {
            return true;
        }
    }

    return false;
}

function reportWindowSize() {
    var currentlyMobile = isMobile();
    if (currentlyMobile == isSetupForMobile) return;
    isSetupForMobile = currentlyMobile;

    for (var tab of ["txt2img", "img2img"]) {
        var button = gradApp().getElementById(tab + '_generate_box');
        var target = gradApp().getElementById(currentlyMobile ? tab + '_results' : tab + '_actions_column');
        target.insertBefore(button, target.firstElementChild);

        gradApp().getElementById(tab + '_results').classList.toggle('mobile', currentlyMobile);
    }
}

window.addEventListener("resize", reportWindowSize);

onUiLoaded(function() {
    reportWindowSize();
});
