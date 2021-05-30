package org.qxdn.akts.dto;

public class Resp {

    Integer coda;

    String msg;

    Object content;

    public static final int SUCCESS = 200;
    public static final int BAD = 400;

    public Integer getCoda() {
        return coda;
    }

    public void setCoda(Integer coda) {
        this.coda = coda;
    }

    public String getMsg() {
        return msg;
    }

    public void setMsg(String msg) {
        this.msg = msg;
    }

    public Object getContent() {
        return content;
    }

    public void setContent(Object content) {
        this.content = content;
    }

    public Resp(){

    }

    public Resp(Integer coda, String msg, Object content) {
        this.coda = coda;
        this.msg = msg;
        this.content = content;
    }

    public static Resp  success(String msg,Object content){
        return new Resp(Resp.SUCCESS,msg,content);
    }

    public static Resp bad(String msg,Object content){
        return new Resp(Resp.BAD,msg,content);
    }
}
