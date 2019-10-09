from django.forms.utils import ErrorList

class CustomErrorList(ErrorList):
    def __str__(self):
        return self.as_divs()
    def as_divs(self):
        if not self: return ''
        return '<ul class="list-group">%s</ul>' % ''.join(['<li class="list-group-item list-group-item-danger">%s</li>' % e for e in self])

