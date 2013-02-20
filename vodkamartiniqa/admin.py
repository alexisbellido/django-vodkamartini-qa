from django.contrib import admin
from vodkamartiniqa.models import Question, Answer
from vodkamartinidrupalimport.models import DrupalQuestionNode, DrupalAnswerComment

#class QuestionsInline(admin.TabularInline):
#    model = Question
#    extra = 4

#class AnswersInline(admin.TabularInline):
#    model = Answer
#    fields = ('answer', 'user', 'votes_up', 'votes_down')

class DrupalQuestionNodeInline(admin.TabularInline):
    model = DrupalQuestionNode
    readonly_fields = ('drupal_uid', 'drupal_nid', 'drupal_path')

    def has_delete_permission(self, request, obj=None):
        return False

class QuestionAdmin(admin.ModelAdmin):
    list_filter = ['created', 'status']
    search_fields = ['title']
    prepopulated_fields = {"slug": ("title", )}
    list_display = ('__unicode__', 'author', 'created', 'status')
    # too expensive because each answer is displaying all users
    #inlines = [AnswersInline]
    exclude = ('voted_up_by', 'voted_down_by')
    readonly_fields = ('asked_to',)
    raw_id_fields = ('author',)
    inlines = [DrupalQuestionNodeInline]

class DrupalAnswerCommentInline(admin.TabularInline):
    model = DrupalAnswerComment
    readonly_fields = ('drupal_uid', 'drupal_nid', 'drupal_cid')

    def has_delete_permission(self, request, obj=None):
        return False


class AnswerAdmin(admin.ModelAdmin):
    list_filter = ['submit_date']
    search_fields = ['answer']
    list_display = ('__unicode__', 'user', 'submit_date')
    exclude = ('voted_up_by', 'voted_down_by')
    readonly_fields = ('question',)
    raw_id_fields = ('user',)
    inlines = [DrupalAnswerCommentInline]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
#admin.site.register(Answer)
