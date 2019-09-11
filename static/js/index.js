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
                var cvs = document.getElementById('showimgcvs');
                fr.readAsDataURL(img);
                fr.onloadend = function(e) {
                    showimg.src = e.target.result;
                    cvs.width = showimg.width;
                    cvs.height = showimg.height;

                    //alert(e.target.result);
                };
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
            console.log(res.rois);
            console.log(res.class_names);
            var cvs = document.getElementById('showimgcvs');
            var ctx = cvs.getContext("2d");
            ctx.clearRect(0, 0, cvs.width, cvs.height);
            ctx.beginPath();
            ctx.lineWidth = "2";
            ctx.strokeStyle = "red";
            for (var i = 0; i < res.rois.length; i++) {
                var y = res.rois[i][0],x = res.rois[i][1],h = res.rois[i][2]-y,w = res.rois[i][3]-x;

                ctx.rect(x, y, w, h);
            }
            ctx.stroke();
            for (var i = 0; i < res.rois.length; i++) { 
                var y = res.rois[i][0],x = res.rois[i][1],h = res.rois[i][2]-y,w = res.rois[i][3]-x;           
                ctx.font = 18;
                var txt = res.class_names[i];
                var width = ctx.measureText(txt).width;
                ctx.fillStyle = 'red';
                ctx.fillRect(x-1, y-13, width+2, 12);
                ctx.textBaseline = 'top';
                ctx.fillStyle = 'black';
                ctx.fillText(txt, x, y-12);
            }
            ctx.stroke();
        }).fail(function(){
            console.log("upload fail");
        });
         
         
    });

});