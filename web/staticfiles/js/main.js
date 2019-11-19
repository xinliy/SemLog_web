


var r;

$(document).ready(function () {

    $.ajaxSetup({
        data: { csrfmiddlewaretoken: token },
    });
    $('#formadd').submit(function () {
        var ip_address = '127.0.0.1';

        $.ajax({
            type: "POST",
            data: { ip_address: ip_address },
            url: "update_database_info/",
            cache: false,
            dataType: "json",
            success: function (result, statues, xml) {
                r=result;
            },
            async:false
            // error: function (xhr, status, error) {
            //     alert(xhr.responseText);
            // }
        });
        return false;
    });




    // Add hide/show for two search pattern
    $("#entity_search").click(function(){
        $("#div_entity_search").show();
        $("#div_event_search").hide();
        $("#div_scan_search").hide();
    });
    $("#event_search").click(function(){
        $("#div_event_search").show();
        $("#div_entity_search").hide();
        $("#div_scan_search").hide();
    });
    $("#scan_search").click(function(){
        $("#div_scan_search").show();
        $("#div_entity_search").hide();
        $("#div_event_search").hide();
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

    var padding_div='<div class="padding grouped fields" ><div class="field"><div class="ui radio checkbox">'+
    '<input type="radio" name="padding_type" checked="checked" value="constant">'+
    '<label>Constant</label></div></div>'+
    '<div class="field"><div class="ui radio checkbox">'+
    '<input type="radio" name="padding_type" value="reflect">'+
    '<label>Reflect</label></div></div>'+
    '<div class="field"><div class="ui radio checkbox">'+
    '<input type="radio" name="padding_type" value="reflect_101">'+
    '<label>Reflect_101</label></div></div>'+
    '<div class="field"><div class="ui radio checkbox">'+
    '<input type="radio" name="padding_type" value="replicate">'+
    '<label>Replicate</label></div></div></div>'

    $(".ui.radio.pad").checkbox({
        onChecked:function(){
            // $(".input_pad").remove();
            // $("#div_resize").append('<input type="text" name="padding_constant_color" class="input_pad" placeholder="constant color for padding">');
            // $("#div_resize").append('<input type="text" name="padding_type" class="input_pad" placeholder="type for padding">');
            $("#div_resize").append(padding_div)
        },
    })

    $(".ui.radio.resize").checkbox({
        onChecked:function(){
            $(".padding.grouped.fields").remove();
        },
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


    var id = 0;

    $("#add_class").click(function () {
        var field = document.createElement("input");
        field.name = "class_id" + id;
        field.type = "text";
        field.placeholder = "Class name";
        $(".class_list").append(field);
        id += 1;


    });
    $("#remove_class").click(function () {
        $('.class_list').children().last().remove()
    })

$('#main_form').on('keyup keypress', function(e) {
  var keyCode = e.keyCode || e.which;
  if (keyCode === 13) { 
    e.preventDefault();
    return false;
  }
});

    $("#search").click(function () {
        var r=""
        $("a.ui.label.transition.visible").each(function(){
            // console.log($(this)[0].outerText)
            // alert($(this)[0].outerText)
            r=r+$(this)[0].outerText+"@"
            })
            // console.log(r)
            var i=document.createElement("input")
            i.type="hidden"
            i.name="database_collection_list"
            i.value=r
            $(".db_input").append(i)
        // $(".ui.label.transition.visible").addClass('red');
    })

$('#main_form').submit(function(e){
    var db_list = Object.keys(r);
    console.log(db_list)
    var stop_submit=0;
    $('a.ui.label.transition.visible').each(function(){

        var input_db=$(this)[0].outerText;

    // Remove old error div
    // if ($(this).parent().hasClass("error")){
    //     console.log('has error div!')
    //     $(this).unwrap()
    // }

    // Get each input
//     var input_db=$(this).val();

//     // if *.*, continue
    if(input_db=="*.*"){
        return true
    }

    // Remove whitespaces
    input_array=input_db.replace(/\s/g, "");
    input_array=input_array.split('.');

    db=input_array[0];
    coll=input_array[1];
    if (input_array.length!=2){

        $(this).addClass('red');
        stop_submit=1;
    }
    else if (db=="*" & coll!="*"){

        $(this).addClass('red');
        stop_submit=1;
    }
    // check if db exists
    else if (!db_list.includes(db)){
        $(this).addClass('red');
        stop_submit=1;
    }
    // check if collection exists
    else if (coll!="*"){
        var collection_list = r[db].sort();
        console.log(collection_list)
        if(!collection_list.includes(coll)){
        $(this).addClass('red');
            stop_submit=1;
        }
    }



    if(stop_submit==1){
        e.preventDefault();
    }
})
})
    // Remove the arrow in the selection input field of choosing collections
    $(".dropdown.icon").remove()

})









