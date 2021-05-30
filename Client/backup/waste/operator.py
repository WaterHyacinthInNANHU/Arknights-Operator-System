# detected_template = self._wait_for_template(['login/main_panel', 'login/close_announcement'],
#                                             max_retry=60, retry_interval=2)
# if detected_template == 'login/close_announcement':
#     self.logger.debug('detected announcement, closing it')
#     self._click_template('login/close_announcement')
# elif detected_template == 'login/main_panel':
#     self.logger.debug('detected main panel, wait for a while in case of incoming announcement')
#     self._wait(2)
#     self._wait_on_networking(15, 2)
#     self._wait(2)
#     if self._is_template_on_screen('login/close_announcement'):
#         self._click_template('login/close_announcement')
# else:
#     raise ValueError('unknown detected template')
# self.logger.debug('wait for a while in case of incoming daily supply')
# self._wait(2)
# self._wait_on_networking(15, 2)
# self._wait(2)
# if self._is_template_on_screen('login/今日配给'):
#     self._click_pos('login/confirm_今日配给')