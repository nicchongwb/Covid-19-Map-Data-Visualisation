$(document).ready( function () {
    var table = $('.dataframe').DataTable();
    $('.dataframe').addClass('display');
    $('.dataframe').wrap('<div class="tableWrapper"></div>');

} );

$('#datafile').change(function(){
    console.log(this.files[0].name);
    var lbl = document.getElementsByTagName('LABEL')[0];
    lbl.innerHTML = this.files[0].name;
});


