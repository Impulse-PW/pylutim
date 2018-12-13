# What is pylutim?

Pylutim is an API wrapper for [Lutim (Let's Upload That IMage)](https://framagit.org/fiat-tux/hat-softwares/lutim) made to be Human-Friendly.

## Example Usage

```py
>>> import pylutim
>>> service = pylutim.controller("http://127.0.0.1:8080")

#Login to the service
>>> service.login("Impulse", "testing")
{'msg': 'You have been successfully logged in.', 'success': True}

#Upload image (path, delete_after_days, delete_after_first_view, keep_exif_tags, encrypt_image)
>>> response = service.upload("/home/impulse/Pictures/Selection_002.png", 1, 1, 0, 1)
>>> response
{'class': <pylutim.lib.pylutim.image object at 0x7f51c03eb8d0>, 'success': True}

#pylutim returns an object you can use to control your image
>>> image = response["class"]

#Download the image, delete_after_first_view is set so this will destroy the image
>>> image.download("/home/impulse/Desktop/test.png")
{'msg': 'Image downloaded!', 'success': True}

#View counter still works though =]
>>> image.get_counter()
{'counter': 1, 'enabled': False, 'success': True}

#Let's try modifying the image (delete_after_days, delete_after_first_view)
#This should not work since we destroyed the image
>>> image.modify(1, 0)
{'msg': "Cannot modify image: image doesn't exist!", 'success': False}
```

<b>Installation</b>
===================

Install with pip:
```
pip install pylutim
```

Install from source:
```
git clone https://github.com/Impulse-PW/pylutim
cd pylutim
sudo python3 setup.py install
```

<b>Like pylutim?</b>
======================

<a href='https://ko-fi.com/M4M4LOV3' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://az743702.vo.msecnd.net/cdn/kofi4.png?v=0' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
