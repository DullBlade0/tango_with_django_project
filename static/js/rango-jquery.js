/**
 * Created by dullblade on 10/09/16.
 */
$(document).ready(function () {
    $("#about-btn").click(function (event) {
        alert("You clicked the button using JQuery!");
    });


    $("p").hover(function () {
        $(this).css('color', 'red');
    },
    function () {
        $(this).css('color', 'blue');
    });


    $("#about-btn").click(function (event) {
    mgstr = $("#msg").html()
    mgstr = mgstr + "ooo"
    $("#msg").html(mgstr)


    });
});

