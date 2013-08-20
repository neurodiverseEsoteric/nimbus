// Globals

// True means used closed the wc dialog.
var __wc_closed = false;

function __wc_refresh() {
  __wc_closed = false;
}

function __wc_jqueryWrapper() {
  if (typeof  jQuery == 'undefined') {// jQuery isn't loaded yet. Get back later
    setTimeout(__wc_jqueryWrapper, 500);
    return;
  }

  // The stick-display control
  (function($){
  $.fn.stickyCounter = function(stats, options){

    var options   = options || {};
    var directory = options && options.directory ? options.directory : 'images';
    var zooming   = false;

    if ($('#sticky').length == 0) {
      var ext = 'png';
      var html = '<div id="sticky" style="display:none;z-index:2147483647;direction:ltr" dir="ltr"> \
                    <table id="sticky_table" dir="ltr" style="border-collapse:collapse; width:100%; height:100%; direction:ltr"> \
                      <tbody> \
                        <tr> \
                          <td style="background:url(' + directory + '/sprite-h.' + ext + ') 0 0 no-repeat; width:20px; height:20px; overflow:hidden;" /> \
                          <td style="background:url(' + directory + '/sprite-h.' + ext + ') 0 -123px repeat-x; height:20px; overflow:hidden;" /> \
                          <td style="background:url(' + directory + '/sprite-h.' + ext + ') -45px -675px no-repeat; width:20px; height:20px; overflow:hidden;" /> \
                        </tr> \
                        <tr> \
                          <td style="background:url(' + directory + '/sprite-v.' + ext + ') 0 0 repeat-y; width:20px; overflow:hidden;" /> \
                          <td style="background:#fff; vertical-align:top;"> \
                            <div id="sticky_content"> \
                            </div> \
                          </td> \
                          <td style="background:url(' + directory + '/sprite-v.' + ext + ') -133px 0 repeat-y;  width:20px; overflow:hidden;" /> \
                        </tr> \
                        <tr> \
                          <td style="background:url(' + directory + '/sprite-h.' + ext + ') 0 -250px no-repeat; width:20px; height:20px; overflow:hidden;" /> \
                          <td style="background:url(' + directory + '/sprite-h.' + ext + ') 0 -422px repeat-x; height:20px; overflow:hidden;" /> \
                          <td style="background:url(' + directory + '/sprite-h.' + ext + ') -48px -550px no-repeat; width:20px; height:20px; overflow:hidden;" /> \
                        </tr> \
                      </tbody> \
                    </table> \
                    <a href="#" title="Close" id="sticky_close" style="position:absolute; top:0; right:0; text-decoration:none"> \
                      <div style="background:url(' + directory + '/sprite-h.' + ext + ') 0 -592px no-repeat; width:30px; height:30px; overflow:hidden;">&nbsp;</div> \
                    </a> \
                  </div>';

      $('body').append(html);

      // Hide on Esc
      $(document).keyup(function(event){
          if (event.keyCode == 27 && $('#sticky:visible').length > 0) hide();
      });

      $('#sticky_close').click(hide);
      $('#sticky').draggable();
    }

    var sticky          = $('#sticky');
    var sticky_table    = $('#sticky_table');
    var sticky_close    = $('#sticky_close');
    var sticky_content  = $('#sticky_content');
    var middle_row      = $('td.ml,td.mm,td.mr');

    show(stats);

    return this;

    function show(stats) {
      if (zooming) return false;
      zooming = true;
      var sticky_width  = options.width;
      var sticky_height = options.height;

      var width       = window.innerWidth || (window.document.documentElement.clientWidth || window.document.body.clientWidth);
      var height      = window.innerHeight || (window.document.documentElement.clientHeight || window.document.body.clientHeight);
      var x           = window.pageXOffset || (window.document.documentElement.scrollLeft || window.document.body.scrollLeft);
      var y           = window.pageYOffset || (window.document.documentElement.scrollTop || window.document.body.scrollTop);
      var window_size = {'width':width, 'height':height, 'x':x, 'y':y}

      var width              = (sticky_width || Math.max(("" + stats.chars).length * 20),20 + 7 * ('' + stats.words).length) + 60;
      var height             = (sticky_height || 30) + 60;
      var d                  = window_size;

      // ensure that newTop is at least 0 so it doesn't hide close button
      var newTop             = 10;
      var newLeft            = 10;
      var curTop             = 0;
      var curLeft            = 0;

      sticky_close.attr('curTop', curTop);
      sticky_close.attr('curLeft', curLeft);
      sticky_close.attr('scaleImg', 'false');

      // If already displayed, just update inner html, don't animate
      if ($('#sticky').is(':visible')) {
        sticky_content.html(statsHtml(stats));
        $('#sticky').show().css({
          opacity : "show",
          width   : width,
          height  : height
        });
        sticky_content.html(statsHtml(stats));
        sticky_close.show();
        zooming = false;
        return;
      }

      $('#sticky').hide().css({
        position: 'fixed',
        top: curTop + 'px',
        left: curLeft + 'px',
        width     : '1px',
        height    : '1px'
      });

      sticky_close.hide();

      sticky_content.html('');

      $('#sticky').animate({
        top     : newTop + 'px',
        left    : newLeft + 'px',
        opacity : "show",
        width   : width,
        height  : height
      }, 500, null, function() {
        sticky_content.html(statsHtml(stats));
        sticky_close.show();
        zooming = false;
      })
      return false;
    }

    function hide() {
      if (zooming) return false;
      zooming         = true;
      $('#sticky').unbind('click');
      sticky_content.html('');
      sticky_close.hide();
      $('#sticky').animate({
        top     : sticky_close.attr('curTop') + 'px',
        left    : sticky_close.attr('curLeft') + 'px',
        opacity : "hide",
        width   : '1px',
        height  : '1px'
      }, 500, null, function() {
        zooming = false;
        if (options.close) {
          options.close(this);
        }
      });
      return false;
    }

    function statsHtml(stats) {
      var a = [];
      a.push('<div id="wcChars" class="');
      if (stats.chars < 140) {
        a.push('wcCharsLess140');
      } else {
        a.push('wcCharsMore140');
      }
      a.push('">');
      a.push(stats.chars);
      a.push('</div>');
      a.push('<div id="wcWords">');
      a.push('W: ');
      a.push('<b>');
      a.push(stats.words);
      a.push('</b>');
      a.push('</div>');
      a.push('<div id="wcLines">');
      a.push('L: ');
      a.push('<b>');
      a.push(stats.lines);
      a.push('</b>');
      a.push('</div>');
      // Add Tweet This
      if (stats.chars > 0) {
        a.push('<div id="tweetThis">');
        a.push('<a target="_blank" href="http://twitter.com/home?status=');
        a.push(encodeURIComponent(stats.text));
        a.push('">');
        a.push('Tweet&nbsp;this');
        a.push('</a>');
        a.push('</div>');
      }
      return a.join('');
    }
  }
  })(jQuery);

  // Application logic
  javascript:(function($){
    // Function: finds selected text on document d.
    // @return the selected text or null
    function f(d){
      var t;
      if (d.getSelection) t = d.getSelection();
      else if(d.selection) t = d.selection.createRange();
      if (t && t.text != undefined) t = t.text;
      if (!t || t == '') {
        $('input[type=text], textarea', d).each(function (i) {
          var s;
          try {
            s = $(this).getSelection().text;
            if (s != '') {
              t = s;
            }
          } catch(e){}
        });
      }
      return t;
    };
    // Function: finds selected text in document d and frames and subframes of d
    // @return the selected text or null
    function g(d){
      var t;
      try{t = f(d);}catch(e){error(e)};
      if (!t || t == '') {
        $('frame, iframe', d).each(function(i){
          // See if there's permission to access this frame. Try the document.location attribute
          try {
            var tmp = this.contentDocument.location;
            // OK, passed
            t = g(this.contentDocument);
          } catch(e){}
        });
      }
      return t;
    };

    function u() {
      if (__wc_closed) return;
      var t = g(document);
      display(t);
    }

    // Updates the display with text
    function display(t){
      if (!t) {
        t = '';
      }
      var s = stats(t.toString());
      $('#__wc_pseudo_display').stickyCounter(s,
          {directory: __wc_base + 's/images',
           close: onClose});
    }

    function onClose() {
      __wc_closed = true;
    }

    /**
     * @returns statistics over the given text
     *    {text: the original text,
     *     chars: number of chars,
     *     words: number of words
     *    }
     */
    function stats(t) {
      var chars = t.length;
      var words = t.split(/\S+/g).length - 1;
      var lines = t.split(/\n/g).length;
      if (chars == 0) {
        lines = 0;
      }
      return {text: t, chars: chars, words: words, lines: lines};
    }

    function addCss(fileName) {
      var link = document.createElement("link");
      link.setAttribute("rel", "stylesheet");
      link.setAttribute("type", "text/css");
      link.setAttribute("href", fileName);
      document.getElementsByTagName("head")[0].appendChild(link);
    }

    function error(m) {
      if (window.console && window.console.error) {
        window.console.error(m);
      }
    }

    addCss(__wc_base + 's/main.css');

    u();
    setInterval(u, 500);
  })(jQuery);
}

__wc_jqueryWrapper();
