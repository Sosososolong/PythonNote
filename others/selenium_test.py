from selenium import webdriver
import time

# 设置火狐的各种属性配置(无界面模式)
firefox_options = webdriver.FirefoxOptions()
firefox_options.headless = True

# 应用属性配置实例化一个浏览器
# driver = webdriver.Firefox(options=firefox_options)
driver = webdriver.Firefox()

# 发送请求
driver.get("http://wwww.baidu.com")

# 截屏
driver.save_screenshot("F:/工作/front/python.project/static/tmp/baidu.png")

# 元素定位方法, 找到id为'kw'的文本框, 输入'python'关键字
driver.find_element_by_id('kw').send_keys('python')
# 找到id为"su"的按钮(搜索按钮)并点击
driver.find_element_by_id('su').click()

# driver.find_element_by_xpath(".//h1/p").text
# 根据链接的文字查询a标签元素
# driver.find_element_by_link_text("下一页>").get_attribute("href")
# 根据链接包含的部分文字查找a标签元素
# driver.find_element_by_partial_link_text("下一页").get_attribute("href")
# find_element_by_tag_name()
# find_element_by_css_selector # #food span.dairy.aged


# driver获取网页的源码字符串
print(driver.page_source) # 浏览器中elements的内容(js执行之后的结果,因为它自己就是浏览器,已经执行了css,js等)

# driver获取cookie
cookies = driver.get_cookies()
print(cookies)
print("*"*100)
# 使用字典推导式
cookies = {i["name"]:i["value"] for i in cookies}
print(cookies)

time.sleep(3)
# driver.close() # 退出当前页
# 退出浏览器
driver.quit()
