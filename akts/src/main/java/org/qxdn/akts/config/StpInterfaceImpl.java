package org.qxdn.akts.config;

import org.qxdn.akts.dao.UserRepository;
import org.qxdn.akts.model.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import cn.dev33.satoken.stp.StpInterface;

import java.util.ArrayList;
import java.util.List;


@Component
public class StpInterfaceImpl implements StpInterface{

    @Autowired
    UserRepository userRepository;

    /**
     * 权限码
     * @param loginId
     * @param loginKey 用于多套账号体系
     * @return
     */
    @Override
    public List<String> getPermissionList(Object loginId, String loginKey) {
        String email = (String)loginId;
        //根据email查user
        User user = userRepository.findUserByEmail(email);
        List<String> list = new ArrayList<>();
        if(user.getRole().equals("user")){
            //基础权限
            list.add("base");
        }
        return list;
    }

    /**
     * 角色
     * @param loginId
     * @param loginKey
     * @return
     */
    @Override
    public List<String> getRoleList(Object loginId, String loginKey) {
        String email = (String)loginId;
        //根据email查user
        User user = userRepository.findUserByEmail(email);
        List<String> list = new ArrayList<>();
        list.add(user.getRole());
        return list;
    }
}
