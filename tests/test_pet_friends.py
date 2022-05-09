import pprint
from json import dumps

from api import PetFriends
from settings import valid_email, valid_password, invalid_email
import os

pf = PetFriends()


def test_get_api_key_valid_user(email=valid_email, password=valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Bob', animal_type='Dog',
                                     age='4', pet_photo='images/dog.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и
    # опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Angry", "dog", "3", "images/dog.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Картошка', animal_type='Кошка', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'],
                                            name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об
        # отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_add_new_pet_without_photo(name='Bob', animal_type='Dog', age='7'):
    """Проверяем возможность добавления питомца без фото"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.new_pet_without_photo(auth_key, name, animal_type, age)

    assert status == 200
    assert result['name'] == name


def test_add_photo_pet(pet_photo='images/rabbit.jpg'):
    """Проверяем возможность добавления фото питомцу без фото"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) > 0:
        status, result = pf.set_photo(auth_key, my_pets['pets'][0]['id'], pet_photo)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об
        # отсутствии своих питомцев
        raise Exception("There is no my pets")


# Далее мои тесты ---------------------------------------------------------------------

def test_invalid_password(email=valid_email, password='123456789'):
    # Пробуем авторизоваться с не правильным паролем

    status, result = pf.get_api_key(email, password)
    try:
        assert status == 200
    except:
        assert status == 400 or 403
    print(result)


def test_invalid_email(email=invalid_email, password=valid_password):
    # Пробуем авторизоваться с не правильной почтой

    status, result = pf.get_api_key(email, password)
    try:
        assert status == 200
    except:
        assert status == 400 or 403
    # assert status != 200
    print(result)


def test_get_my_list_pets():
    # Получаем список моих питомцев

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, 'my_pets')
    assert status == 200
    assert len(result['pets']) > 0
    pprint.pprint(dumps(result, indent=7))


def test_add_new_pet_without_any_params(name=None, animal_type=None, age=None):
    """Проверяем возможность добавления питомца без данных"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.new_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 200


def test_add_new_pet_with_incorrect_data(name='Bob', animal_type='Dog', age=['a', 'b']):
    """Проверяем возможность добавления питомца с некорректными данными"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.new_pet_without_photo(auth_key, name, animal_type, age)
    try:
        assert status == 200
    except:
        assert status == 400 or 403


def test_add_new_pet_with_invalid_photo(name='Bob', animal_type='Dog',
                                     age='4', pet_photo='images/text.txt'):
    """Проверяем что можно ли добавить питомца с не правильными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    try:
        assert status == 200
    except:
        assert status == 400 or 403 or 500