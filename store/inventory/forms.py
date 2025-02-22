from django import forms
from .models import  Products, Category
import unicodedata
from django.utils.text import slugify
import re
import unicodedata
from django.core.exceptions import ValidationError

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        labels = {
            'name': 'Name',
            'description': 'Description',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sweet wine',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter general information Etc.',
                'rows': 3,  
            }),
            
        }
        error_messages = {
            # Puedes agregar mensajes de error personalizados aquí si es necesario
        }
        
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Normalizar el nombre: eliminar acentos, espacios extra y convertir a minúsculas
            normalized_name = ''.join(c for c in unicodedata.normalize('NFD', name)
                                    if unicodedata.category(c) != 'Mn')
            normalized_name = re.sub(r'\s+', '', normalized_name.lower())
            
            instance = self.instance
            # Buscar categorías existentes con nombres similares
            existing_categories = Category.objects.exclude(id=instance.id)
            for category in existing_categories:
                category_normalized = ''.join(c for c in unicodedata.normalize('NFD', category.name)
                                            if unicodedata.category(c) != 'Mn')
                category_normalized = re.sub(r'\s+', '', category_normalized.lower())
                if category_normalized == normalized_name:
                    raise ValidationError(f"Ya existe una categoría similar: '{category.name}'")
        return name

        
class ProductsForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['code', 'category', 'name', 'description', 'price', 'status']
        labels = {
            'code': 'Code',
            'category': 'Category',
            'name': 'Product Name',
            'description': 'Description',
            'price': 'Price',
            'status': 'State',
            'cost': 'Cost',
            'quantity': 'Amount',
        }
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Wine001',
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sweet wine',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter general information Etc.',
                'rows': 3,
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the price of the product',
                'step': '0.01',
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
            }, choices=[
                (1, 'active'),
                (0, 'idle')
            ]),
            
            'cost': forms.NumberInput(attrs={
                'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control'}),
        }
        error_messages = {
            'code': {
                'required': 'This field is required.',
                'max_length': 'This field cannot exceed 100 characters.',
            },
            'category': {
                'required': 'This field is required',
            },
            'name': {
                'required': 'This field is required',
            },
            'description': {
                'required': 'This field is required',
            },
            'price': {
                'required': 'This field is required',
                'invalid': 'Please enter a valid price.',
            },
            'status': {
                'required': 'This field is required',
                'invalid': 'Please enter a valid status.',
            }
        }
    def __init__(self, *args, **kwargs):
        super(ProductsForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            if field.errors:
                field.widget.attrs['class'] += ' is-invalid'
                
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Sort the category queryset alphabetically
        self.fields['category'].queryset = Category.objects.all().order_by('name')
        #Set the field as non-editable
        self.fields['status'].disabled = True
    
    
    @staticmethod
    def normalize_text(text):
        if text:
            #Remove accents and convert to lowercase
            text = ''.join(c for c in unicodedata.normalize('NFD', text)
                        if unicodedata.category(c) != 'Mn')
            # Remove special characters and spaces
            text = re.sub(r'[^\w]', '', text.lower())
        return text
    
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        code = cleaned_data.get('code')

        if name and code:
            normalized_name = self.normalize_text(name)
            normalized_code = self.normalize_text(code)

            #Get the current instance if we are editing
            instance_id = self.instance.pk if self.instance.pk else None

            # Check name duplicates
            name_duplicates = Products.objects.all()
            if instance_id:
                name_duplicates = name_duplicates.exclude(pk=instance_id)
            
            for product in name_duplicates:
                if self.normalize_text(product.name) == normalized_name:
                    self.add_error('name', "A product with a similar name already exists.")
                    raise ValidationError("There is already a product with a similar name.")

            # Check code duplicates
            code_duplicates = Products.objects.filter(code__iexact=normalized_code)
            if instance_id:
                code_duplicates = code_duplicates.exclude(pk=instance_id)
            if code_duplicates.exists():
                self.add_error('code', "A product already exists with this code.")
                raise ValidationError("A product already exists with this code.")

        return cleaned_data
    