


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
                // $("#collection_selector").empty();


                // Add DB$ALL options
                // for (i=0;i<k.length;i++){
                //         var option = document.createElement("option");
                //         option.text = k[i] + "$" + "ALL";
                //         c = k[i] + "$" + "ALL";
                //         var v = "<input type='text' name=" + "database_collection" + i.toString() + "ALL" + " value=" + c + " hidden>";
                //         $("#collection_selector").append(option)                   
                // }

                // // Add every options
                // for (i = 0; i < k.length; i++) {
                //     var collection_list = result[k[i]].sort();
                //     for (j = 0; j < collection_list.length; j++) {
                //         var option = document.createElement("option");
                //         option.text = k[i] + "$" + collection_list[j];
                //         c = k[i] + "$" + collection_list[j];
                //         var v = "<input type='text' name=" + "database_collection" + i.toString() + j.toString() + " value=" + c + " hidden>";

                //         $("#collection_selector").append(option)
                //     }
                // }

    //         $(document).ready(function () {
    //             var db_list = Object.keys(result);
    //         $('#main_form').submit(function(e){
    //             var stop_submit=0;
    //             $(".error").remove();
    //             $('.class_db').each(function(){


    //             // Get each input
    //             var input_db=$(this).val();

    //             // if *.*, continue
    //             if(input_db=="*.*"){
    //                 return true
    //             }

    //             // Remove whitespaces
    //             input_db=input_db.trim();

    //             // Split with dot
    //             input_array=input_db.split('.');

    //             if (input_array.length!=2){
    //                 alert("Please use 'db.collection' to add scope.");
    //                 $(this).wrap("<div class='field error'></div>");
    //                 stop_submit=1;
    //             }

    //             db=input_array[0];
    //             coll=input_array[1];

    //             // check if "*.collection1" appears
    //             if (db=="*" & coll!="*"){
    //                 $(this).wrap("<div class='field error'></div>");
    //                 stop_submit=1;
    //             }
    //             // check if db exists
    //             else if (!db_list.includes(db)){
    //                 console.log(db_list);
    //                 alert("Available databases: "+db_list);
    //                 $(this).wrap("<div class='field error'></div>");
    //                 stop_submit=1;
    //             }
    //             // check if collection exists
    //             else{
    //                 var collection_list = result[db].sort();
    //                 if(!collection_list.includes(coll)){
    //                     console.log(collection_list);
    //                     alert("Current db: "+db+" Available collections: "+collection_list);
    //                     $(this).wrap("<div class='field error'></div>");
    //                     stop_submit=1;
    //                 }
    //             }



    //             if(stop_submit==1){
    //                 e.preventDefault();
    //         }
    //     })
    // })})
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

    $(".ui.radio.pad").checkbox({
        onChecked:function(){
            $(".input_pad").remove();
            $("#div_resize").append('<input type="text" name="padding_constant_color" class="input_pad" placeholder="constant color for padding">');
            $("#div_resize").append('<input type="text" name="padding_type" class="input_pad" placeholder="type for padding">');
        },
    })

    $(".ui.radio.resize").checkbox({
        onChecked:function(){
            $(".input_pad").remove();
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
    $("#add_db").click(function () {
        var flag_add=1;
        $('.class_db').each(function(){
            var input_db=$(this).val();
            if(input_db=="*.*"){
                flag_add=0;
                alert("You have selected all collections!")
            }
        })
        if(flag_add==1){
        var field = document.createElement("input");
        field.name = "db_id" + id;
        field.type = "text";
        field.className="class_db";
        field.placeholder = "db id";
        $(".db_list").append(field);
        id += 1;
        }


    });
    $("#remove_db").click(function () {
        $('.db_list').children().last().remove()
    })


$('#main_form').submit(function(e){
    console.log("search clicked!")
    console.log(r)
    var db_list = Object.keys(r);
    var stop_submit=0;
    $('.class_db').each(function(){

    // Remove old error div
    if ($(this).parent().hasClass("error")){
        console.log('has error div!')
        $(this).unwrap()
    }

    // Get each input
    var input_db=$(this).val();

    // if *.*, continue
    if(input_db=="*.*"){
        return true
    }

    // Remove whitespaces
    input_array=input_db.replace(/\s/g, "");
    input_array=input_array.split('.');

    db=input_array[0];
    coll=input_array[1];
    if (input_array.length!=2){
        alert("Please use 'db.collection' to add scope.");
        $(this).wrap("<div class='field error'></div>");
        stop_submit=1;
    }
    // check if "*.collection1" appears
    else if (db=="*" & coll!="*"){
        $(this).wrap("<div class='field error'></div>");
        stop_submit=1;
    }
    // check if db exists
    else if (!db_list.includes(db)){
        console.log(db_list);
        alert("Available databases: "+db_list);
        $(this).wrap("<div class='field error'></div>");
        stop_submit=1;
    }
    // check if collection exists
    else if (coll!="*"){
        var collection_list = r[db].sort();
        console.log(collection_list)
        if(!collection_list.includes(coll)){
            console.log(collection_list);
            alert("Current db: "+db+" Available collections: "+collection_list);
            $(this).wrap("<div class='field error'></div>");
            stop_submit=1;
        }
    }



    if(stop_submit==1){
        e.preventDefault();
    }
})
})

})









