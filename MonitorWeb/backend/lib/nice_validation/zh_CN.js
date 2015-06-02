/*********************************
 * Themes, rules, and i18n support
 * Locale: Chinese; ÖÐÎÄ
 *********************************/
(function ($) {
    /* Global configuration
     */
    $.validator.config({
        //stopOnError: false,
        //theme: 'yellow_right',
        defaultMsg: "{0}¸ñÊ½²»ÕýÈ·",
        loadingMsg: "ÕýÔÚÑéÖ¤...",
        
        // Custom rules
        rules: {
            digits: [/^\d+$/, "ÇëÊäÈëÊý×Ö"]
            ,letters: [/^[a-z]+$/i, "{0}Ö»ÄÜÊäÈë×ÖÄ¸"]
            ,tel: [/^(?:(?:0\d{2,3}[- ]?[1-9]\d{6,7})|(?:[48]00[- ]?[1-9]\d{6}))$/, "µç»°¸ñÊ½²»ÕýÈ·"]
            ,mobile: [/^1[3-9]\d{9}$/, "ÊÖ»úºÅ¸ñÊ½²»ÕýÈ·"]
            ,email: [/^(?:[a-z0-9]+[_\-+.]?)*[a-z0-9]+@(?:([a-z0-9]+-?)*[a-z0-9]+\.)+([a-z]{2,})+$/i, "ÓÊÏä¸ñÊ½²»ÕýÈ·"]
            ,qq: [/^[1-9]\d{4,}$/, "QQºÅ¸ñÊ½²»ÕýÈ·"]
            ,date: [/^\d{4}-\d{1,2}-\d{1,2}$/, "ÇëÊäÈëÕýÈ·µÄÈÕÆÚ,Àý:yyyy-mm-dd"]
            ,time: [/^([01]\d|2[0-3])(:[0-5]\d){1,2}$/, "ÇëÊäÈëÕýÈ·µÄÊ±¼ä,Àý:14:30»ò14:30:00"]
            ,ID_card: [/^[1-9]\d{5}[1-9]\d{3}((0\d)|(1[0-2]))(([0|1|2]\d)|3[0-1])((\d{4})|\d{3}[A-Z])$/, "ÇëÊäÈëÕýÈ·µÄÉí·ÝÖ¤ºÅÂë"]
            ,url: [/^(https?|ftp):\/\/[^\s]+$/i, "ÍøÖ·¸ñÊ½²»ÕýÈ·"]
            ,postcode: [/^[1-9]\d{5}$/, "ÓÊÕþ±àÂë¸ñÊ½²»ÕýÈ·"]
            ,chinese: [/^[\u0391-\uFFE5]+$/, "ÇëÊäÈëÖÐÎÄ"]
            ,username: [/^\w{3,12}$/, "ÇëÊäÈë3-12Î»Êý×Ö¡¢×ÖÄ¸¡¢ÏÂ»®Ïß"]
            ,password: [/^[0-9a-zA-Z]{6,16}$/, "ÃÜÂëÓÉ6-16Î»Êý×Ö¡¢×ÖÄ¸×é³É"]
            ,accept: function (element, params){
                if (!params) return true;
                var ext = params[0];
                return (ext === '*') ||
                       (new RegExp(".(?:" + (ext || "png|jpg|jpeg|gif") + ")$", "i")).test(element.value) ||
                       this.renderMsg("Ö»½ÓÊÜ{1}ºó×º", ext.replace('|', ','));
            }
            
        }
    });

    /* Default error messages
     */
    $.validator.config({
        messages: {
            required: "{0}²»ÄÜÎª¿Õ",
            remote: "{0}ÒÑ±»Ê¹ÓÃ",
            integer: {
                '*': "ÇëÊäÈëÕûÊý",
                '+': "ÇëÊäÈëÕýÕûÊý",
                '+0': "ÇëÊäÈëÕýÕûÊý»ò0",
                '-': "ÇëÊäÈë¸ºÕûÊý",
                '-0': "ÇëÊäÈë¸ºÕûÊý»ò0"
            },
            match: {
                eq: "{0}Óë{1}²»Ò»ÖÂ",
                neq: "{0}Óë{1}²»ÄÜÏàÍ¬",
                lt: "{0}±ØÐëÐ¡ÓÚ{1}",
                gt: "{0}±ØÐë´óÓÚ{1}",
                lte: "{0}±ØÐëÐ¡ÓÚ»òµÈÓÚ{1}",
                gte: "{0}±ØÐë´óÓÚ»òµÈÓÚ{1}"
            },
            range: {
                rg: "ÇëÊäÈë{1}µ½{2}µÄÊý",
                gt: "ÇëÊäÈë´óÓÚ»òµÈÓÚ{1}µÄÊý",
                lt: "ÇëÊäÈëÐ¡ÓÚ»òµÈÓÚ{1}µÄÊý"
            },
            checked: {
                eq: "ÇëÑ¡Ôñ{1}Ïî",
                rg: "ÇëÑ¡Ôñ{1}µ½{2}Ïî",
                gt: "ÇëÖÁÉÙÑ¡Ôñ{1}Ïî",
                lt: "Çë×î¶àÑ¡Ôñ{1}Ïî"
            },
            length: {
                eq: "ÇëÊäÈë{1}¸ö×Ö·û",
                rg: "ÇëÊäÈë{1}µ½{2}¸ö×Ö·û",
                gt: "ÇëÊäÈë´óÓÚ{1}¸ö×Ö·û",
                lt: "ÇëÊäÈëÐ¡ÓÚ{1}¸ö×Ö·û",
                eq_2: "",
                rg_2: "",
                gt_2: "",
                lt_2: ""
            }
        }
    });

    /* Themes
     */
    var TPL_ARROW = '<span class="n-arrow"><b>¡ô</b><i>¡ô</i></span>';
    $.validator.setTheme({
        'simple_right': {
            formClass: 'n-simple',
            msgClass: 'n-right'
        },
        'simple_bottom': {
            formClass: 'n-simple',
            msgClass: 'n-bottom'
        },
        'yellow_top': {
            formClass: 'n-yellow',
            msgClass: 'n-top',
            msgArrow: TPL_ARROW
        },
        'yellow_right': {
            formClass: 'n-yellow',
            msgClass: 'n-right',
            msgArrow: TPL_ARROW
        },
        'yellow_right_effect': {
            formClass: 'n-yellow',
            msgClass: 'n-right',
            msgArrow: TPL_ARROW,
            msgShow: function($msgbox, type){
                var $el = $msgbox.children();
                if ($el.is(':animated')) return;
                if (type === 'error') {
                    $el.css({
                        left: '20px',
                        opacity: 0
                    }).delay(100).show().stop().animate({
                        left: '-4px',
                        opacity: 1
                    }, 150).animate({
                        left: '3px'
                    }, 80).animate({
                        left: 0
                    }, 80);
                } else {
                    $el.css({
                        left: 0,
                        opacity: 1
                    }).fadeIn(200);
                }
            },
            msgHide: function($msgbox, type){
                var $el = $msgbox.children();
                $el.stop().delay(100).show().animate({
                    left: '20px',
                    opacity: 0
                }, 300, function(){
                    $msgbox.hide();
                });
            }
        }
    });
})(jQuery);