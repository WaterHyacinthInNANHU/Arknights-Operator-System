package org.qxdn.akts.dto;

import javax.validation.constraints.Email;

public class AEmail {

    @Email
    private String email;

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }
}
