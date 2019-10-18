$(document).ready(function () {

    $.ajaxSetup({
        data: { csrfmiddlewaretoken: token },
    });
    $('#formadd').submit(function () {
        var ip_address = $("#ip_address").val();

        $.ajax({
            type: "POST",
            data: { ip_address: ip_address },
            url: "update_database_info/",
            cache: false,
            dataType: "json",
            success: function (result, statues, xml) {
                $("#collection_selector").empty();
                var k = Object.keys(result);
                k=k.filter(function(e){return e !=="semlog_web"})

                // Add DB$ALL options
                for (i=0;i<k.length;i++){
                        var option = document.createElement("option");
                        option.text = k[i] + "$" + "ALL";
                        c = k[i] + "$" + "ALL";
                        var v = "<input type='text' name=" + "database_collection" + i.toString() + "ALL" + " value=" + c + " hidden>";
                        $("#collection_selector").append(option)                   
                }

                // Add every options
                for (i = 0; i < k.length; i++) {
                    var collection_list = result[k[i]].sort();
                    for (j = 0; j < collection_list.length; j++) {
                        var option = document.createElement("option");
                        option.text = k[i] + "$" + collection_list[j];
                        c = k[i] + "$" + collection_list[j];
                        var v = "<input type='text' name=" + "database_collection" + i.toString() + j.toString() + " value=" + c + " hidden>";

                        $("#collection_selector").append(option)
                    }
                }
            },
            error: function (xhr, status, error) {
                alert(xhr.responseText);
            }
        });
        return false;
    });



    // Add hide/show for two search pattern
    $("#entity_search").click(function(){
        $("#div_entity_search").show();
        $("#div_event_search").hide();
    });
    $("#event_search").click(function(){
        $("#div_event_search").show();
        $("#div_entity_search").hide();
    });

    var id = 0;
    $("#view_add").click(function () {
        var field = document.createElement("input");
        field.name = "view_object_id" + id;
        field.type = "text";
        field.placeholder = "View object id";
        $(".view_object_list").append(field);
        id += 1;


    });
    $("#view_remove").click(function () {
        $('.view_object_list').children().last().remove()
    })



    $("#button_ip").click(function () {
        $("#main_form").removeAttr("hidden")

    })

    var id = 0;
    $("#add").click(function () {
        var field = document.createElement("input");
        field.name = "object_id" + id;
        field.type = "text";
        field.placeholder = "Object id";
        $(".object_list").append(field);
        id += 1;


    });
    $("#remove").click(function () {
        $('.object_list').children().last().remove()
    })

    $("#search").click(function () {
        var r=""
        $("a.ui.label.transition.visible").each(function(){
            console.log($(this)[0].outerText)
            // alert($(this)[0].outerText)
            r=r+$(this)[0].outerText+"@"
        })
        console.log(r)
        var i=document.createElement("input")
        i.type="hidden"
        i.name="database_collection_list"
        i.value=r
        $(".db_input").append(i)
    })



})






