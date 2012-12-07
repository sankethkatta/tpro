$("#tweetinput input").focus();
var loading = $("#loading");
var button = $("#tweetinput button");
var result_list = $("#result_list");
var template = function(user, img, bio) {
	return '<li > <div class="span3"> <a href="http://twitter.com/'+user+'" target="_blank" > <img class="img-circle" src="'+img+'"  data-content="'+bio+'" data-original-title="Biography"> <iframe allowtransparency="true" frameborder="0" scrolling="no" src="//platform.twitter.com/widgets/follow_button.html?screen_name='+user+'&show_count=false" style="width:100%; height:25px;"></iframe> </div><!-- /.span3 --> </li>'

};
$("#tweetinput").submit(function(e) {
    e.preventDefault();
    var query = $(this).serialize();
    button.attr("disabled", "disabled");
    button.html("Analyzing...");
    loading.css("display", "block");

    $.ajax({
        url: "/analyze",
        type: "POST",
	timeout: 300000,
        dataType: "JSON",
        data: query
    }).done(function(data) {
       if (data.length === 0) {
	   loading.css("display", "none");
	  flashMessage();
	} else {
	   loading.css("display", "none");
           buildTable(data); 
        }
    }).error(function(jqXHR, textStatus) {
	console.log(textStatus);		
    });
});

var FLASH = $("#flash")
var flashMessage = function() {
    FLASH.slideDown(500).delay(3000).slideUp(500);
    button.removeAttr("disabled");
    button.html("Analyze");
};

var buildTable = function(data) {
    button.removeAttr("disabled");
    button.html("Analyze");
    result_list.children().remove()
    for (i = 0; i < data.length; i++) {
	result_list.append(template(data[i].user, data[i].img, data[i].bio));
    };
	$("img").popover({trigger: "hover", placement:"top"})
};
var TWITTER_BUTTON = '<script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src="//platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script>'
