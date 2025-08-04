# products/factories.py
import factory
from factory.django import DjangoModelFactory
from faker import Faker
import random
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from products.models import Product, Comment, Category
from django.utils.text import slugify
from django.conf import settings  # <-- Added for file path resolution
import os  # <-- Added for file path resolution

faker = Faker('fa_IR')

# Expanded real-world product data in Persian
PRODUCT_DATA = [
    # Mobile and Tablets
    {
        'title': 'موبایل اپل iPhone 14',
        'short_description': 'آیفون ۱۴ با پردازنده A15 Bionic، دوربین دوگانه پیشرفته و قابلیت تشخیص تصادف.',
        'description': 'گوشی هوشمند آیفون ۱۴ با نمایشگر ۶.۱ اینچی Super Retina XDR OLED، پردازنده قدرتمند A15 Bionic، و سیستم دوربین دوگانه ۱۲ مگاپیکسلی با دیافراگم ƒ/1.5. این گوشی از قابلیت‌های Emergency SOS و Crash Detection بهره می‌برد. باتری با دوام تا ۲۰ ساعت پخش ویدئو و مقاومت در برابر آب و گرد و غبار با استاندارد IP68.',
        'price': 42_000_000,
        'category_name': 'موبایل',
    },
    {
        'title': 'موبایل سامسونگ Galaxy S23',
        'short_description': 'گلکسی S23 با پردازنده Snapdragon 8 Gen 2، دوربین ۵۰ مگاپیکسلی و طراحی مدرن.',
        'description': 'سامسونگ گلکسی S23 با نمایشگر Dynamic AMOLED 2X و نرخ تازه‌سازی ۱۲۰ هرتز، تجربه بصری فوق‌العاده‌ای ارائه می‌دهد. پردازنده Snapdragon 8 Gen 2 for Galaxy، عملکردی بی‌نظیر برای بازی و کارهای سنگین فراهم می‌کند. سیستم دوربین سه‌گانه با سنسور اصلی ۵۰ مگاپیکسلی و زوم اپتیکال ۳ برابر، به شما اجازه می‌دهد تصاویری با جزئیات خیره‌کننده ثبت کنید. بدنه مقاوم با محافظ Gorilla Glass Victus 2 و استاندارد IP68.',
        'price': 35_000_000,
        'category_name': 'موبایل',
    },
    {
        'title': 'لپ‌تاپ لنوو IdeaPad 5',
        'short_description': 'لپ‌تاپ سبک و قدرتمند با پردازنده Core i7 و صفحه نمایش Full HD مناسب برای کارهای روزمره.',
        'description': 'لپ‌تاپ لنوو IdeaPad 5 با طراحی ظریف و وزن کم، گزینه‌ای عالی برای دانشجویان و کاربران حرفه‌ای است. مجهز به پردازنده نسل دوازدهم Intel Core i7، ۸ گیگابایت رم و ۲۵۶ گیگابایت حافظه SSD، عملکردی روان و سریع را تضمین می‌کند. صفحه نمایش ۱۵.۶ اینچی Full HD با حاشیه‌های باریک و باتری با شارژدهی بالا، کاربری آن را لذت‌بخش می‌کند.',
        'price': 25_000_000,
        'category_name': 'کالای دیجیتال',
    },
    {
        'title': 'هدفون سونی WH-1000XM5',
        'short_description': 'هدفون بی‌سیم با قابلیت حذف نویز فعال و کیفیت صدای بی‌نظیر.',
        'description': 'هدفون بی‌سیم سونی WH-1000XM5 جدیدترین نسل از هدفون‌های محبوب سونی است که با قابلیت حذف نویز پیشرفته، به شما اجازه می‌دهد تا در هر محیطی روی موسیقی خود تمرکز کنید. طراحی ارگونومیک، وزن سبک، و باتری با شارژدهی ۳۰ ساعته، آن را برای استفاده طولانی‌مدت ایده‌آل کرده است. کیفیت صدای فوق‌العاده و پشتیبانی از کدک‌های صوتی با کیفیت بالا از دیگر ویژگی‌های برجسته این هدفون است.',
        'price': 15_000_000,
        'category_name': 'کالای دیجیتال',
    },
    # New products and categories
    {
        'title': 'تلویزیون هوشمند ال‌جی ۵۵ اینچ',
        'short_description': 'تلویزیون ۵۵ اینچ با کیفیت تصویر ۴K و سیستم عامل webOS برای سرگرمی نامحدود.',
        'description': 'تلویزیون هوشمند ال‌جی با صفحه نمایش ۵۵ اینچ و رزولوشن ۴K، تصاویری با وضوح و رنگ‌های خیره‌کننده نمایش می‌دهد. با پشتیبانی از HDR و فناوری‌های پیشرفته تصویر، جزئیات را به بهترین شکل ممکن نشان می‌دهد. سیستم صوتی Dolby Atmos و سیستم عامل webOS، تجربه‌ای سینمایی و هوشمند را برای شما به ارمغان می‌آورد. طراحی مینیمال و حاشیه‌های کم، زیبایی خاصی به محیط خانه شما می‌بخشد.',
        'price': 38_000_000,
        'category_name': 'لوازم خانگی',
    },
    {
        'title': 'یخچال ساید بای ساید سامسونگ',
        'short_description': 'یخچال فریزر ساید بای ساید با ظرفیت بالا و سیستم خنک‌کننده Twin Cooling Plus.',
        'description': 'یخچال ساید بای ساید سامسونگ با طراحی مدرن و ظرفیت ۶۰۰ لیتر، فضای کافی برای نگهداری مواد غذایی خانواده‌های پرجمعیت را فراهم می‌کند. فناوری Twin Cooling Plus با ایجاد دو جریان هوای مجزا، از مخلوط شدن بوی مواد غذایی جلوگیری کرده و رطوبت را در سطح بهینه نگه می‌دارد. مجهز به یخساز و آبسردکن اتوماتیک، کمپرسور اینورتر دیجیتال کم‌صدا و کم‌مصرف.',
        'price': 65_000_000,
        'category_name': 'لوازم خانگی',
    },
    {
        'title': 'اسپیکر قابل حمل JBL Flip 6',
        'short_description': 'اسپیکر بلوتوثی ضدآب و گرد و غبار با صدای قدرتمند و باتری طولانی.',
        'description': 'اسپیکر قابل حمل JBL Flip 6 با طراحی جمع‌وجور و صدای استریو، همراه ایده‌آل شما در سفر و مهمانی است. با استاندارد IP67، در برابر آب و گرد و غبار مقاوم بوده و می‌توانید آن را بدون نگرانی در ساحل یا استخر استفاده کنید. باتری داخلی آن تا ۱۲ ساعت پخش موسیقی را پشتیبانی می‌کند. قابلیت اتصال دو اسپیکر JBL به یکدیگر برای صدای قوی‌تر.',
        'price': 4_500_000,
        'category_name': 'کالای دیجیتال',
    },
    {
        'title': 'کتاب هنر ظریف بی‌خیالی',
        'short_description': 'کتابی پرطرفدار از مارک منسن درباره پیدا کردن معنای واقعی خوشبختی.',
        'description': 'کتاب هنر ظریف بی‌خیالی، با رویکردی متفاوت به مبحث موفقیت و خودیاری می‌پردازد. نویسنده در این کتاب به شما نشان می‌دهد که کلید خوشبختی، مثبت اندیشی بی‌حد و حصر نیست، بلکه پذیرش محدودیت‌ها و انتخاب‌های درست در زندگی است. زبانی صریح و طنزآمیز دارد و دیدگاه شما را نسبت به مسائل زندگی تغییر می‌دهد.',
        'price': 120_000,
        'category_name': 'کتاب',
    },
    {
        'title': 'شلوار جین مردانه زارا',
        'short_description': 'شلوار جین جذب با طراحی کلاسیک و پارچه کشی برای راحتی بیشتر.',
        'description': 'شلوار جین مردانه از برند زارا، با برش اسلیم فیت و رنگ آبی تیره، یک انتخاب عالی برای استایل روزمره و غیررسمی است. پارچه کشی با کیفیت بالا، راحتی فوق‌العاده‌ای را در طول روز فراهم می‌کند. این شلوار به راحتی با انواع تی‌شرت و پیراهن ست می‌شود.',
        'price': 1_800_000,
        'category_name': 'لباس',
    },
]

# Real-world comments for products
COMMENT_REVIEWS = {
    'موبایل اپل iPhone 14': [
        {'text': 'عالیه، دوربینش بی‌نظیره و سرعتش فوق‌العاده است. از خریدم خیلی راضی‌ام.', 'stars': 5},
        {'text': 'باتریش نسبت به آیفون ۱۳ بهتر شده ولی انتظار بیشتری داشتم. در کل خوبه.', 'stars': 4},
        {'text': 'قیمتش خیلی بالاست ولی کیفیت ساخت و نرم‌افزارش بی‌رقیبه.', 'stars': 4},
        {'text': 'خیلی خوش‌دست و سبک هست. عملکردش هم برای بازی‌ها عالیه.', 'stars': 5},
        {'text': 'نسبت به قیمتش ارزش خرید داره. تنها مشکلش شارژ دهی متوسط باتری است.', 'stars': 3},
    ],
    'موبایل سامسونگ Galaxy S23': [
        {'text': 'صفحه نمایشش واقعاً عالیه، رنگ‌هاش خیلی زنده‌ست. دوربینش هم تو شب معرکه است.', 'stars': 5},
        {'text': 'خیلی خوش‌دست و سبک هست. عملکردش هم برای بازی‌ها عالیه.', 'stars': 5},
        {'text': 'نسبت به قیمتش ارزش خرید داره. تنها مشکلش شارژ دهی متوسط باتری است.', 'stars': 3},
        {'text': 'طراحیش خیلی خوبه و توی دست احساس خوبی میده. عملکردش هم عالیه.', 'stars': 4},
    ],
    'لپ‌تاپ لنوو IdeaPad 5': [
        {'text': 'لپ‌تاپ خوبیه، سرعتش برای کارهای من کافیه. طراحی ساده و زیبایی داره.', 'stars': 4},
        {'text': 'قیمتش مناسبه ولی بدنه پلاستیکیش حس خوبی نمیده.', 'stars': 3},
        {'text': 'عالیه، برای کارهای دانشجویی و روزمره فوق‌العاده است.', 'stars': 5},
    ],
    'هدفون سونی WH-1000XM5': [
        {'text': 'بهترین هدفونیه که تا حالا داشتم. حذف نویزش فوق‌العاده است و کیفیت صداش عالیه.', 'stars': 5},
        {'text': 'شارژش خیلی خوب نگه میداره و خیلی راحت روی گوش قرار می‌گیره. پیشنهاد می‌کنم.', 'stars': 5},
        {'text': 'قیمت بالایی داره ولی برای موزیک‌دوست‌ها ارزشش رو داره.', 'stars': 4},
        {'text': 'کیفیت صداش در حد انتظارم نبود. حذف نویزش خوبه ولی صداش نه.', 'stars': 3},
    ],
    'تلویزیون هوشمند ال‌جی ۵۵ اینچ': [
        {'text': 'کیفیت تصویرش عالیه، رنگ‌ها واقعا طبیعی و زیبا هستند.', 'stars': 5},
        {'text': 'بسته‌بندی مناسبی داشت و ارسال سریع بود.', 'stars': 4},
    ],
    'یخچال ساید بای ساید سامسونگ': [
        {'text': 'یخچال خیلی جادار و خوبیه. قسمت فریزرش هم عالیه.', 'stars': 5},
        {'text': 'صدای موتور کمی زیاده ولی در کل راضی‌ام.', 'stars': 3},
    ],
    'اسپیکر قابل حمل JBL Flip 6': [
        {'text': 'صدای قوی و بیس خوبی داره. برای سفر عالیه.', 'stars': 5},
        {'text': 'واقعا ضدآب و مقاومه. بدون ترس توی حمام استفاده می‌کنم.', 'stars': 5},
    ],
    'کتاب هنر ظریف بی‌خیالی': [
        {'text': 'کتاب فوق‌العاده‌ای بود، دیدگاهم رو نسبت به زندگی عوض کرد.', 'stars': 5},
        {'text': 'ترجمه‌اش یکم سنگین بود ولی در کل ارزش خوندن داره.', 'stars': 4},
    ],
    'شلوار جین مردانه زارا': [
        {'text': 'جنسش عالیه و خیلی راحت هست. اندازه‌اش هم کاملاً فیت بود.', 'stars': 5},
        {'text': 'رنگش بعد از چند بار شستشو کمی کمرنگ شد.', 'stars': 3},
    ],
    'کتاب ملت عشق': [
        {'text': 'کتابی پر از درس و پند. قلم نویسنده واقعا جذابه و خواننده رو با خودش همراه می‌کنه.', 'stars': 5},
        {'text': 'داستانش خیلی عمیق و تاثیرگذار بود. برای من کتابی فراموش‌نشدنی شد.', 'stars': 5},
    ],
}


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ('slug',)

    name = factory.Iterator(sorted(list(set(item['category_name'] for item in PRODUCT_DATA))))
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name, allow_unicode=True))


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product
        # Create unique products from the predefined list
        django_get_or_create = ('title',)

    _product_data = factory.Iterator(PRODUCT_DATA)

    title = factory.LazyAttribute(lambda o: o._product_data['title'])
    description = factory.LazyAttribute(lambda o: o._product_data['description'])
    short_description = factory.LazyAttribute(lambda o: o._product_data['short_description'])
    price = factory.LazyAttribute(lambda o: o._product_data['price'])
    category = factory.LazyAttribute(
        lambda o: Category.objects.get_or_create(
            name=o._product_data['category_name'],
            defaults={'slug': slugify(o._product_data['category_name'], allow_unicode=True)}
        )[0]
    )

    status = 'avl'
    stock_quantity = factory.LazyFunction(lambda: random.randint(1, 50))

    @factory.lazy_attribute
    def image(self):
        # Corrected file path
        placeholder_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'placeholder.jpg')
        try:
            with open(placeholder_path, 'rb') as f:
                return ContentFile(f.read(), name=faker.file_name(extension='jpg'))
        except FileNotFoundError:
            return None


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    is_staff = False
    is_superuser = False

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password('password123')
        if create:
            self.save()


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    product = factory.SubFactory(ProductFactory)
    user = factory.SubFactory(UserFactory)

    @factory.lazy_attribute
    def text(self):
        return random.choice(COMMENT_REVIEWS.get(self.product.title, [{'text': faker.text(), 'stars': 4}]))['text']

    @factory.lazy_attribute
    def stars(self):
        return str(
            random.choice(COMMENT_REVIEWS.get(self.product.title, [{'text': '', 'stars': random.randint(1, 5)}]))[
                'stars'])

    is_verified = True
