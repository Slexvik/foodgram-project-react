from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tags(models.Model):
    """

    """
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.MAX_LENGTH_NAME_TAG,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет',
        unique=True,
        max_length=settings.MAX_LENGTH_COLOR_TAG,
    )
    slug = models.SlugField(
        verbose_name='Слаг тэга',
        unique=True,
        max_length=settings.MAX_LENGTH_SLUG_TAG,
        # db_index=False,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name}, цвет: {self.color}'


class Ingredients(models.Model):
    """

    """
    name = models.CharField(
        verbose_name='Наименование',
        unique=True,
        max_length=settings.MAX_LENGTH_NAME_INGREDIENT,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=settings.MAX_LENGTH_UNIT_MEASUREMENT,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient',
            ),
            # models.CheckConstraint(
            #     check=models.Q(name__length__gt=0),
            #     name="\n%(app_label)s_%(class)s_name is empty\n",
            # ),
            # models.CheckConstraint(
            #     check=models.Q(measurement_unit__length__gt=0),
            #     name="\n%(app_label)s_%(class)s_measurement_unit is empty\n",
            # ),
        ]

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'

    # def clean(self):
    #     self.name = self.name.lower()
    #     self.measurement_unit = self.measurement_unit.lower()
    #     super().clean()


class Recipes(models.Model):
    """

    """

    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=settings.MAX_LENGTH_NAME_RECIPE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name='Тэги',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name='Состав блюда',
        through='RecipeIngredient',
        related_name="recipes",
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        max_length=settings.MAX_LENGTH_TEXT_RECIPE,
        )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        upload_to='recipe_images/',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                settings.MIN_COOKING_TIME,
                message='Время приготовления не должно быть менее 1 минуты',
            ),
            MaxValueValidator(
                settings.MAX_COOKING_TIME,
                message='Время приготовления не должно быть более суток',
            ),
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        # default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_for_author',
            ),
            # models.CheckConstraint(
            #     check=Q(name__length__gt=0),
            #     name="\n%(app_label)s_%(class)s_name is empty\n",
            # ),
        )

    def __str__(self):
        return f'{self.name} - {self.author}'


class RecipeIngredient(models.Model):
    """

    """
    recipe = models.ForeignKey(
        to=Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipes',
    )
    ingredient = models.ForeignKey(
        to=Ingredients,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredients',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                settings.MIN_AMOUNT,
                message='Выберите индигриент',
            ),
            MaxValueValidator(
                settings.MAX_AMOUNT,
                message='Блюдо содержит больше 100 индигриентов',
            ),
        ],
    )

    class Meta:
        verbose_name = 'Состав рецепта'
        verbose_name_plural = 'Состав рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=["recipe",   "ingredient"],
                name="unique_ingredient_in_recipe",
            )
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name}'
            f'{self.amount} {self.ingredient.measurement_unit}'
        )


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        default_related_name = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipes',
            )
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Корзина пользователя'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Список рецептов'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart',
            )
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe}'
