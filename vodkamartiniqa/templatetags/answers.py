from django import template
from vodkamartiniqa.forms import AnswerForm
from vodkamartiniqa.models import Answer
from django.template.loader import render_to_string
from django.core import urlresolvers
from django.utils.encoding import smart_unicode

register = template.Library()

class BaseAnswerNode(template.Node):
    def __init__(self, object_expr=None, as_varname=None, num=0):
        if object_expr is None:
            raise template.TemplateSyntaxError("Answer nodes must be given a literal object.")
        self.as_varname = as_varname
        self.object_expr = object_expr
        self.num = num

    # the @classmethod decorator returns a class method for function. The class, in variable cls, is this class.
    @classmethod
    def handle_token(cls, parser, token):
        """Class method to parse get_answer_list/count/form and return a Node."""
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])

        # used for these
        # {% get_whatever for obj as varname %}
        # {% get_answer_count for object as answer_count %}
        elif len(tokens) == 5 or len(tokens) == 6:
            if tokens[3] != 'as':
                raise template.TemplateSyntaxError("Third argument in %r must be 'as'" % tokens[0])
            if len(tokens) == 5:
                if tokens[4] != 'answer_count':
                    raise template.TemplateSyntaxError("Fourth argument in %r must be 'answer_count'" % tokens[0])
                num = 0
            if len(tokens) == 6:
                num = tokens[5]
            return cls(
                object_expr = parser.compile_filter(tokens[2]),
                as_varname = tokens[4],
                num = num,
            )
        else:
            raise template.TemplateSyntaxError("%r tag requires 5 arguments" % tokens[0])

    def render(self, context):
        qs = self.get_query_set(context)
        context[self.as_varname] = self.get_context_value_from_queryset(context, qs)
        return ''

    def get_object(self, context):
        if self.object_expr:
            try:
                return self.object_expr.resolve(context)
            except template.VariableDoesNotExist:
                return None

    def get_query_set(self, context):
        obj = self.get_object(context)
        if not obj:
            return Answer.objects.none()
        # important for reducing queries
        # see https://docs.djangoproject.com/en/dev/ref/models/querysets/#select-related
        # in other cases could use values()
        # see https://docs.djangoproject.com/en/dev/topics/db/optimization/#don-t-retrieve-things-you-don-t-need
        if self.num:
            qs = Answer.objects.select_related().filter(question=obj).filter(is_public=True).filter(is_removed=False).order_by('submit_date')[:self.num]
        else:
            qs = Answer.objects.select_related().filter(question=obj).filter(is_public=True).filter(is_removed=False).order_by('submit_date')
        return qs

    def get_context_value_from_queryset(self, context, qs):
        """Subclasses should override this."""
        raise NotImplementedError

class AnswerCountNode(BaseAnswerNode):
    """Insert a count of answers into the context."""
    def get_context_value_from_queryset(self, context, qs):
        return qs.count()

class AnswerListNode(BaseAnswerNode):

    """Insert a list of answers into the context."""
    def get_context_value_from_queryset(self, context, qs):
        return list(qs)

class RenderAnswerFormNode(template.Node):
    """Render the answer form directly"""

    def __init__(self, object_expr=None, as_varname=None):
        if object_expr is None:
            raise template.TemplateSyntaxError("Answer nodes must be given a literal object.")
        self.as_varname = as_varname
        self.object_expr = object_expr

    # the @classmethod decorator returns a class method for function. The class, in variable cls, is RenderAnswerFormNode.
    @classmethod
    def handle_token(cls, parser, token):
        """Class method to parse render_answer_form and return a Node."""
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])

        # {% render_answer_form for obj %}
        if len(tokens) == 3:
            return cls(object_expr=parser.compile_filter(tokens[2]))

    def get_target_pk(self, context):
        obj = self.get_object(context)
        return obj.pk

    def get_form(self, context):
        obj = self.get_object(context)
        if obj:
            return AnswerForm(obj)
        else:
            return None

    def get_object(self, context):
        if self.object_expr:
            try:
                return self.object_expr.resolve(context)
            except template.VariableDoesNotExist:
                return None

    def render(self, context):
        object_pk = self.get_target_pk(context)
        if object_pk:
            template = "vodkamartiniqa/answer_form.html"
            context.push()
            formstr = render_to_string(template, {"form" : self.get_form(context)}, context)
            context.pop()
            return formstr
        else:
            return ''

@register.simple_tag
def answer_form_target():
    """
    Get the target URL for the answer form.

    Example::

        <form action="{% answer_form_target %}" method="post">
    """
    return urlresolvers.reverse("vodkamartiniqa.views.questions.post_answer")

@register.tag
def render_answer_form(parser, token):
    """
    Render the answer form (as returned by ``{% render_answer_form %}``) through
    the ``vodkamartiniqa/answer_form.html`` template.

    Syntax::

        {% render_answer_form for [object] %}
    """
    return RenderAnswerFormNode.handle_token(parser, token)

@register.tag
def get_answer_count(parser, token):
    """
    Gets the answer count for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_answer_count for [object] as [varname]  %}

    Example usage::

        {% get_answer_count for object as answer_count %}

    """
    return AnswerCountNode.handle_token(parser, token)

@register.tag
def get_answer_list(parser, token):
    """
    Gets the list of answers for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_answer_list for [object] as [varname] [num] %}

    Example usage::

        {% get_answer_list for event as answer_list 5 %}
        {% for answer in answer_list %}
            ...
        {% endfor %}

    """
    return AnswerListNode.handle_token(parser, token)
