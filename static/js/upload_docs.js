if(!$){
$ = django.jQuery;
}

$(document).ready(function() {
    $('.custom-file-input').on('change', function() {
        verify_uploaded_doc(this);
    });
    $('#upload_doc').on('click', function(event){
        document.activeElement.blur();
        isvalid = true;
        $(".custom-file-input").each(function(i,ele){
        console.log(ele);
            if($("#"+ele.id).val()==''){
//                console.log("here...");
                isvalid = false;
                Swal.fire({icon: 'warning', title: 'Oops...', text: "Please upload document!",}).then((result) => { $("#"+ele.id).focus(); });
                return false;
            }
        });
        if(isvalid){
            Swal.fire({
                title: 'Are you sure?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                text: 'Upload the document!',
                confirmButtonText: 'Yes'
                }).then((result) => {
                if (result.isConfirmed) {
                    $('#upload_doc').prop("disabled", true);
                    $("#doc_upload_form").submit();
                }
            });
        }
        event.preventDefault();
    });
});

function verify_uploaded_doc(this_ele) {
    const size = (this_ele.files[0].size / 1024 / 1024).toFixed(2);
    const status_ele = $('#'+$(this_ele).attr('id')+'-status');
    const file_name = (this_ele.files[0].name).toLowerCase();
    const file_ext = file_name.substring(file_name.lastIndexOf('.') + 1)
    var config = $("#doc_type").val();
    var type_matched = false;
    var size_matched = false;
    $("#"+this_ele.id).next('label').html(file_name);
    config = JSON.parse(config.replace(/'/g,'"'));
    config.forEach(function(v,i){
        if (v['type']==file_ext){
            type_matched = true;
            if (v['size']>=size){
                status_ele.html('Valid file size and type');
                status_ele.css('color','green');
                size_matched = true;
            }
            else{
                status_ele.html('Invalid file size : '+size+'MB');
                status_ele.css('color','red');
            }
            return false;
        }
    });
    if (type_matched && size_matched){
        $('#upload_doc').prop('disabled',false);
    }
    else{
        if (!type_matched)
        $('#'+$(this_ele).attr('id')+'-status').html('Invalid file type');
        status_ele.css('color','red');
        $('#upload_doc').prop('disabled',true);
    }
}
