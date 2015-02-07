'use strict';

function submit_booklet(url) {
    /* Check there is a title */
    if ($('#id_title').val() === '') {
        $('#div_id_title').addClass('has-error');
        $('#error_1_id_title').remove();
        $('#id_title').after('<span id="error_1_id_title" class="help-block"><strong>Tämä kenttä vaaditaan.</strong></span>');
    } else {
        $('#div_id_title').removeClass('has-error');
        $('#error_1_id_title').remove();
    }

    /* Check there are songs in the booklet */
    if ($('#id_search').val() === '') {
        $('#div_id_search').addClass('has-error');
        $('#error_1_id_search').remove();
        $('#id_search').after('<span id="error_1_id_search" class="help-block"><strong>Tämä kenttä vaaditaan.</strong></span>');
    } else {
        $('#div_id_search').removeClass('has-error');
        $('#error_1_id_search').remove();
    }

    /* If there is a title and songs in the booklet */
    if ($('#id_title').val() !== '' && $('#id_search').val() !== '') {
        var ret = $("#id_search").val().split(',');
        var array = [];
        for (var i = 0; i < ret.length; i++) {
            if (!isNaN(parseInt(ret[i], 10))) {
                array.push(parseInt(ret[i], 10));
            }
        }
        $("#id_search").val(array).trigger("change");
        var data = {
            title: $("#id_title").val(),
            songs: array,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
        };

        /* Front page text */
        if ($('#id_front_page_text').val() !== '') {
            data['front_page_text'] = $('#id_front_page_text').val();
        } else {
            data['front_page_text'] = '';
        }
        /* Front page image url */
        if ($('#id_front_page_image_url').val() !== '') {
            data['front_page_image_url'] = $('#id_front_page_image_url').val();
        } else {
            data['front_page_image_url'] = '';
        }

        $.ajax({
            type: 'POST',
            url: url,
            data: data
        }).done(function(response) {
            /* Redirect to booklet_list */
            window.location.href = response;
        }).fail(function(response) {
            console.log(response);
        });
    }
}

function searchFunction() {
    var numberOfImages = 5;
    var flickerAPI = "http://api.flickr.com/services/feeds/photos_public.gne?jsoncallback=?";

    // Clear the old images
    $("#thumbnailContainer").empty();
    $("#thumbnailContainer").html("<strong>Haetaan kuvia..</strong>");

    $.getJSON(flickerAPI, {
        tags: $("#flickr_search").val(),
        tagmode: "any",
        format: "json"
    })
        .done(function(data) {
            $("#thumbnailContainer").empty();
            if (data.items.length === 0) {
                $("#leftCarouselControl").hide();
                $("#rightCarouselCountrol").hide();
                $("#thumbnailContainer").html("<strong>Ei hakutuloksia.</strong>");
            } else {
                $("#leftCarouselControl").show();
                $("#rightCarouselControl").show();

                $.each(data.items, function(i, item) {
                    if (i % numberOfImages === 0) {
                        if (i === 0) {
                            $('#thumbnailContainer').append('<div class="item active"><div class="row">');
                        } else {
                            $('#thumbnailContainer').append('<div class="item"><div class="row">');
                        }
                    } else {
                        $('.row:last').append('<div class="col-sm-3"><a id="link-'+i+'" href="#" data-link="' + item.media.m + '">');
                        $("<img class=\"img-thumbnail\">").attr("src", item.media.m).appendTo("#thumbnailContainer a:last");
                        $('#link-'+i).on('click', function(e) {
                            e.preventDefault();
                            $('#id_front_page_image_url').val($('#link-'+i).attr('data-link'));
                        });
                    }
                });
            }
        });
}

$(document).ready(function() {
    var preload_data = [],
        selected = [];

    $('#thumbnailCarousel').carousel({
        interval: false
    });

    /* Get songs */
    $.ajax({
        type: "GET",
        url: "/getSongs/",
        success: function(data) {
            for (var i = 0; i < data.length; i++) {
                preload_data[i] = {};
                preload_data[i]['id'] = data[i].pk;
                preload_data[i]['text'] = data[i].fields.title;
            }
        },
        dataType: 'json'
    });

    /* Flickr search toggle */
    $('#flickr_toggle').on('click', function(e){
        e.preventDefault();
        $('#id_flickr').slideToggle();
    });

    /* Flickr search */
    $('#flickr_search').on('keyup', function(e) {
    if (e.which == 13) {
        e.preventDefault();
        searchFunction();
    }
});
    /* Submit handler */
    $('#choose').on('click', function() {
        if ($('#choose').val() == "Lähetä") {
            submit_booklet("/create_booklet/");
        } else {
            var url = "/update_booklet/" + $('#booklet_id').attr("value") + "/";
            submit_booklet(url);
        }

    });

    /* Song selection select2 initialization */
    $("#id_search").select2({
        dropdownAutoWidth: true,
        tags: preload_data
    });

    $("#id_search").on("change", function() {

        $("#id_search").html($("#id_search").val());
    });

    $("#id_search").select2("container").find("ul.select2-choices").sortable({
        containment: 'parent',
        start: function() {
            $("#id_search").select2("onSortStart");
        },
        update: function() {
            $("#id_search").select2("onSortEnd");
        }
    });


});