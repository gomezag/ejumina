document.addEventListener('DOMContentLoaded', function() {
    var plusButtons = document.querySelectorAll('.form-control-stepup');
    var minusButtons = document.querySelectorAll('.form-control-stepdown');

    plusButtons.forEach(function(button) {
        button.addEventListener('click', function(el) {
            var targetId = el.target.getAttribute('data-target');
            stepOnUp(document.getElementById(targetId));
        });
    });

    minusButtons.forEach(function(button) {
        button.addEventListener('click', function(el) {
            var targetId = el.target.getAttribute('data-target');
            stepOnDown(document.getElementById(targetId));
        });
    });
});

function stepOnUp(inp){
    inp.stepUp();
    inp.dispatchEvent(new Event('input'));
}
function stepOnDown(inp){
    inp.stepDown();
    inp.dispatchEvent(new Event('input'));
}