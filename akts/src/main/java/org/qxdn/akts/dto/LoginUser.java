package org.qxdn.akts.dto;

import javax.validation.constraints.Email;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;

import org.qxdn.akts.config.valid.LoginValid;
import org.qxdn.akts.config.valid.RegisterValid;
import org.qxdn.akts.config.valid.ResetPasswordValid;

public class LoginUser {

    private Long id;

    @NotBlank(groups = {RegisterValid.class})
    private String username;

    @Email(groups = {RegisterValid.class,LoginValid.class,ResetPasswordValid.class})
    private String email;

    @NotBlank(groups = {RegisterValid.class,LoginValid.class,ResetPasswordValid.class})
    private String password;

    private String role;

    //邮件验证码
    @NotNull(groups = {RegisterValid.class,ResetPasswordValid.class})
    private Integer code;

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public Integer getCode() {
        return code;
    }

    public void setCode(Integer code) {
        this.code = code;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }


}
