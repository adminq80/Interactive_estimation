#!/usr/bin/env python
from random import random
from time import sleep

from selenium import webdriver


def main():
    browser = webdriver.Firefox(executable_path='/home/abdul/Downloads/geckodriver')
    browser.get('http://localhost:8000/solo/')
    submit = browser.find_element_by_xpath('/html/body/div[2]/div[2]/form/input[2]')
    submit.submit()

    sleep(2)
    # for i in range(1, 6):
    #     browser.execute_script("document.querySelector('.overview-{} > .row > .nextButton').click()".format(i))
    #     sleep(1)
    browser.execute_script("document.querySelector('.overview-5 > .row > .nextButton').click()")

    browser.execute_script("document.querySelector('#id_q1_0').checked = true")
    browser.execute_script('document.querySelector("#id_q2").value = 1')

    browser.execute_script("document.querySelector('#id_q4_1').checked = true")
    browser.execute_script("document.querySelector('#id_q5_0').checked = true")
    browser.execute_script('document.querySelector("button.nextButton").click()')
    sleep(2)
    logos = []
    while 'exit' not in browser.current_url:
        browser.execute_script("document.querySelector('input[name=guess]').value = {};".format(round(random(), 2)))
        img = browser.find_element_by_class_name('img-responsive')
        logos.append(img.get_attribute('src'))
        browser.execute_script("document.querySelector('#submit').click()")
        sleep(1)
        browser.execute_script("document.querySelector('#submit').click()")
        sleep(2)

    username = browser.find_element_by_xpath('//p[2]/strong')
    feedback = browser.find_element_by_id('feedback')
    feedback.send_keys('TEST Selenium')
    feedback.submit()
    with open('control.logs', 'a') as f:
        f.write('{},{}\n'.format(username.text, ','.join(logos)))
    browser.quit()


if __name__ == '__main__':
    main()
