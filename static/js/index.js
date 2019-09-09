$(document).ready(function(){

    
    
    $("#file").change(function(){
        var img = this.files[0];
        if(!(img.type.indexOf('image')==0 && img.type && /\.(?:jpg|png|jpeg)$/.test(img.name)) ){
            alert('圖片只能是jpg,jpeg,png');
            return ;
        }else{

            if(window.FileReader) {

                var fr = new FileReader();
                var showimg = document.getElementById('showimg');
                fr.readAsDataURL(img);
                fr.onloadend = function(e) {
                    showimg.src = e.target.result;
                    //alert(e.target.result);
                };
                showimg.style.display = 'block';
            }
        }

    });
    
     $('#Detect').click(function(){
         var src = $('#showimg').attr('src');
         alert(src);
         $.ajax({
            url: '/detect_image',
            type: 'POST',
            data:{
                'img': src
            },
            // async: false,
            cache: false,
            //contentType: false,
            //processData: false
        }).done(function(res){
            alert('rois:' + res.rois+'\nclass_names:' + res.class_names);
        }).fail(function(){
            console.log("upload fail");
         });
         
         
     });


});