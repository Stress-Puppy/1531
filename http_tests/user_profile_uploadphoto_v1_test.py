import pytest

from http_tests.route_wrappers_test import *

'''
Given a URL of an image on the internet, crops the image within bounds (x_start, y_start) 
and (x_end, y_end). Position (0,0) is the top left.

Parameters:(token, img_url, x_start, y_start, x_end, y_end)
Return Type:{}

InputError when any of:
    img_url returns an HTTP status other than 200.
    any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL.
    Image uploaded is not a JPG
'''

@pytest.fixture
def reg_user():
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def test_img():
    image = {
             'url' : 'https://cdn.shopify.com/s/files/1/0051/8992/7005/products/Accessories_StickerWhite-1_800x@2x.jpg',
             'width' : 750,
             'height' : 1000
            }
    return image

@pytest.fixture
def test_img_2():
    image = {
             'url' : 'https://upload.wikimedia.org/wikipedia/commons/5/59/Frog_illustration.jpg',
             'width' : 709,
             'height' : 591
            }
    return image

@pytest.fixture
def png_img():
    image = {
             'url' : 'http://nucleus.unsw.edu.au/etc/clientlibs/unsw-common/unsw-assets/img/social/UNSWlogo-opengraph-squaresafe.png',
             'width' : 1200,
             'height' : 630
            }
    return image

@pytest.fixture
def AccessError():
    return 403

@pytest.fixture
def InputError():
    return 400

def test_success_no_crop(reg_user, test_img):
    clear_v2()
    token = reg_user(0)['token']
    img = test_img
    return_val = user_profile_uploadphoto_v1(token, img['url'], 0, 0, img['width'], img['height'])
    assert return_val == {}

def test_success_valid_crop(reg_user, test_img):
    clear_v2()
    token = reg_user(0)['token']
    img = test_img
    w = int(img['width']/2)
    h = int(img['height']/2)
    return_val = user_profile_uploadphoto_v1(token, img['url'], 0, 0, w, h)
    assert return_val == {}

def test_repeated_success(reg_user, test_img, test_img_2):
    clear_v2()

    token = reg_user(0)['token']

    img = test_img

    w = img['width']
    h = img['height']
    user_profile_uploadphoto_v1(token, img['url'], 0, 0, w, h)

    img = test_img_2

    w = img['width']
    h = img['height']
    return_val = user_profile_uploadphoto_v1(token, img['url'], 0, 0, w, h)

    assert return_val == {}

def test_non_jpg(reg_user, png_img, InputError):
    clear_v2()
    token = reg_user(0)['token']
    img = png_img
    upload_request = user_profile_uploadphoto_v1(token, img['url'], 0, 0, img['width'], img['height'])
    assert upload_request.status_code == InputError

def test_invalid_dimensions(reg_user, test_img, InputError):
    clear_v2()
    token = reg_user(0)['token']
    img = test_img
    w = img['width']
    h = img['height']
    # Test each coordinate being invalid separately
    upload_request = user_profile_uploadphoto_v1(token, img['url'], w+1, 0, w, h)
    assert upload_request.status_code == InputError
    upload_request = user_profile_uploadphoto_v1(token, img['url'], 0, h+1, w, h)
    assert upload_request.status_code == InputError
    upload_request = user_profile_uploadphoto_v1(token, img['url'], 0, 0, w+1, h)
    assert upload_request.status_code == InputError
    upload_request = user_profile_uploadphoto_v1(token, img['url'], 0, 0, w, h+1)
    assert upload_request.status_code == InputError
    upload_request = user_profile_uploadphoto_v1(token, img['url'], -1, 0, w, h)
    assert upload_request.status_code == InputError
    upload_request = user_profile_uploadphoto_v1(token, img['url'], 0, -1, w, h)
    assert upload_request.status_code == InputError
    upload_request = user_profile_uploadphoto_v1(token, img['url'], 0, 0, -1, h)
    assert upload_request.status_code == InputError
    upload_request = user_profile_uploadphoto_v1(token, img['url'], 0, 0, w, -1)
    assert upload_request.status_code == InputError

def test_invalid_url(reg_user, InputError):
    clear_v2()
    token = reg_user(0)['token']
    upload_request = user_profile_uploadphoto_v1(token, 'https://bogus/url/v1', 100, 100, 200, 200)
    assert upload_request.status_code == InputError

def test_non_200_status_code(reg_user, InputError):
    clear_v2()
    token = reg_user(0)['token']
    upload_request = user_profile_uploadphoto_v1(token, 'https://webcms3.cse.unsw.edu.au/COMP1532/21T1/', 100, 100, 200, 200)
    assert upload_request.status_code == InputError

def test_invalid_token(reg_user, test_img, AccessError):
    clear_v2()
    reg_user(0)
    img = test_img
    w = img['width']
    h = img['height']
    upload_request = user_profile_uploadphoto_v1('Invalid token', img['url'], 0, 0, w, h)
    assert upload_request.status_code == AccessError