def login_user(web_server, browser, user):
    """Logs user in"""
    browser.visit(web_server + "/login")
    browser.fill("username", user.email)
    browser.fill("password", user._fb_excluded.password)
    browser.find_by_name("login_email").click()
    assert browser.is_element_present_by_css("#nav-logout")
