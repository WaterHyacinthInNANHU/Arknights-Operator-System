package org.qxdn.akts.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import cn.dev33.satoken.interceptor.SaRouteInterceptor;
import cn.dev33.satoken.router.SaRouterUtil;
import cn.dev33.satoken.stp.StpUtil;

@Configuration
public class SaTokenConfigure implements WebMvcConfigurer {
    /**
     * 使用全局拦截的形式，方便以后替换
     */
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        // 注册路由拦截器，自定义规则
        registry.addInterceptor(new SaRouteInterceptor((request, response, handler) -> {
            // 根据路由划分模块，不同模块不同鉴权
            SaRouterUtil.match("/resetPassword", () -> StpUtil.checkRole("user"));
            SaRouterUtil.match("/resetPassword", () -> StpUtil.checkRole("user"));
        })).addPathPatterns("/**");
        WebMvcConfigurer.super.addInterceptors(registry);
    }
}
