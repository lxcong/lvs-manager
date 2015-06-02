/**
 * demo: 
 * 1.$("#limittext").limittext(); 
 * 2.$("#limittext").limittext({"limit":1});
 * 3.$("#limittext").limittext({"limit":1,"fill":"......","morefn":{"status":true}});
 * 4.$("#limittext").limittext({"limit":1,"fill":"......","morefn":{"status":true,"moretext":"更多","lesstext":"隐藏部分","fullfn":function(){alert("more")},"lessfn":function(){alert("less")}}})
 * 5.$("#limittext").limittext({"limit":1,"fill":"......","morefn":{"status":true}}).limit("all");
 * @param {Object} opt
 * {
 *        limit:30,//显示文字个数
 *        fill:'...'//隐藏时候填充的文字
 *        morefn:{
 *            status:false,//是否启用更多
 *         moretext: "(more)",//隐藏部分文字时候显示的文字
 *         lesstext:"(less)",//全部文字时候显示的文字
 *         cssclass:"limittextclass",//启用更多的A标签的CSS类名
 *         lessfn:function(){},//当文字为更少显示时候回调函数
 *         fullfn:function(){}//当文字为更多时候回调函数
 * }
 * @author Lonely
 * @link http://www.liushan.net
 * @Download:http://down.liehuo.net
 * @version 0.2
 */
jQuery.fn.extend({
  limittext:function(opt){
      opt=$.extend({
        "limit":30,
        "fill":"..."
    },opt);
    opt.morefn=$.extend({
            "status": false,
            "moretext": "(more)",
            "lesstext":"(less)",
            "cssclass": "limittextclass",
            "lessfn": function(){
            },
            "fullfn": function(){
            }
    },opt.morefn);
    var othis=this;
    var $this=$(othis);
    var body=$this.data('body');
    if(body==null){
        body=$this.html();
        $this.data('body',body);
    }
    var getbuttom=function(showtext){
        return "<a href='javascript:;' class='"
        +opt.morefn.cssclass+"'>"
        +showtext
        +"<a>";
    }
    this.limit=function(limit){
        if(body.length<=limit||limit=='all'){
            var showbody=body+(opt.morefn.status?getbuttom(opt.morefn.lesstext):"");
        }else{
            if(!opt.morefn.status){
                var showbody=body.substring(0,limit)
                +opt.fill;
            }else{
                var showbody=body.substring(0,limit)
                +opt.fill
                +getbuttom(opt.morefn.moretext);
            }
        }
        $this.html(showbody);
    }
    this.limit(opt.limit);
    $("."+opt.morefn.cssclass).live("click",function(){
        if($(this).html()==opt.morefn.moretext){
            showbody=body
            +getbuttom(opt.morefn.lesstext);
            $this.html(showbody);
            opt.morefn.fullfn();
        }else{
            othis.limit(opt.limit);
            opt.morefn.lessfn();
        }
    });
    return this;
  }
});