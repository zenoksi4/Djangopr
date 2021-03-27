from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone


User = get_user_model()


class Category(models.Model):

    name = models.CharField(max_length=255, verbose_name="Ім'я категорії")
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

    def get_fields_for_filter_in_template(self):
        return ProductFeatures.objects.filter(
            category=self,
            use_in_filter=True
        ).prefetch_related('category').value('feature_key', 'feature_measure', 'feature_name', 'filter_type')



class Product(models.Model):

    category = models.ForeignKey(Category, verbose_name="Категорія", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name="Найменування")
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name="Зображення")
    description = models.TextField(verbose_name="Опис", null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Ціна")

    def __str__(self):
        return self.title

    def get_model_name(self):
        return self.__class__.__name__.lower()

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

#характеристики
class ProductFeatures(models.Model):

    RADIO = 'radio'
    CHECKBOX = 'checkbox'

    FILTER_TYPE_CHOICES = (
        (RADIO, 'Радіокнопка'),
        (CHECKBOX, 'Чекбокс')
    )
    feature_key = models.CharField(max_length=100, verbose_name='Ключ характеристики')
    feature_name = models.CharField(max_length=255, verbose_name='Найменування характеристики')
    category = models.ForeignKey(Category, verbose_name='Категорія', on_delete=models.CASCADE)
    postfix_for_value = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Постфікс для значення',
        help_text=f'Наприклад для характеристики "Години роботи" до'
                  f' значення можна добавити постфікс "годин", і як результат - значення "10 годин"'
    )
    use_in_filter = models.BooleanField(
        default=False,
        verbose_name='Використовувати фільтрації товарів в шаблоні'
    )
    filter_type = models.CharField(
        max_length=20,
        verbose_name='Тип фільтра',
        default=CHECKBOX,
        choices=FILTER_TYPE_CHOICES
    )

    filter_measure = models.CharField(
        max_length=50,
        verbose_name='Одиниця вимірювання для фільтра',
        help_text='Одиниця вимірювання для конкретного фільтра. Наприклад "Частота процессора (Ghz). '
                  'Одиницею вимірювання буде інформація в дужках"'
    )

    def __str__(self):
        return f'Категорія - "{self.category.name}" | Характеристика - "{self.feature_name}"'

#перевірка характеристик
class ProductFeatureValidators(models.Model):

    category = models.ForeignKey(Category, verbose_name='Категорія', on_delete=models.CASCADE)
    feature = models.ForeignKey(
        ProductFeatures, verbose_name='Характеристика', null=True, blank=True, on_delete=models.CASCADE
    )
    feature_value = models.CharField(
        max_length=255, unique=True, null=True, blank=True, verbose_name='Значення характеристики'
    )

    def __str__(self):
        if not self.feature:
            return f'Валідатор категорії "{self.category.name}" - характеристика не вибрана'
        return f'Валідатор категорії "{self.category.name} |' \
               f'Характеристика - "{self.feature.feature_name}" | '\
               f'Значення - "{self.feature_value}"'


class CartProduct(models.Model):

    user = models.ForeignKey("customer", verbose_name="Покупець", on_delete=models.CASCADE)
    cart = models.ForeignKey("cart", verbose_name="Корзина", on_delete=models.CASCADE, related_name='related_products')
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Загальна ціна")

    def __str__(self):
        return "Продукт: {} (для корзини)".format(self.product.title)

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.product.price
        super().save(*args, **kwargs)


class Cart(models.Model):

    owner = models.ForeignKey("Customer", null=True, verbose_name="Власник", on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, default=0,  decimal_places=2, verbose_name="Загальна ціна")
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)




class Customer(models.Model):

    user = models.ForeignKey(User, verbose_name="Користувач", on_delete=models.CASCADE)
    phone = models.CharField(max_length=28, verbose_name="Номер телефона", null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name="Адрес", null=True, blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Замовлення покупця', related_name='related_customer')

    def __str__(self):
        return "Покупець: {} {}".format(self.user.first_name, self.user.last_name)



#Модель Замовлення
class Order(models.Model):
    #Статуси Замовлень
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    #способи вивозу Замовлення
    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Нове замовлення'),
        (STATUS_IN_PROGRESS, 'Замовлення в обробці'),
        (STATUS_READY, 'Замовлення готове'),
        (STATUS_COMPLETED, 'Замовлення виконане')
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовивоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey(Customer, verbose_name='Покупець', related_name='related_orders', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name="Ім'я")
    last_name = models.CharField(max_length=255, verbose_name="Фамілія")
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name='Адреса', null=True, blank=True)
    status = models.CharField(
        max_length=100,
        verbose_name='Статус замовлення',
        choices=STATUS_CHOICES,
        default=STATUS_NEW
    )
    buying_type = models.CharField(
        max_length=100,
        verbose_name='Тип замовлення',
        choices=BUYING_TYPE_CHOICES,
        default=BUYING_TYPE_SELF
    )
    comment = models.TextField(verbose_name='Коментарій до замовлення', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата створення замовлення')
    order_date = models.DateField(verbose_name='Дата отримання замовлення', default=timezone.now)

    def __str__(self):
        return str(self.id)
