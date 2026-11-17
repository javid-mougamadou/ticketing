from django.contrib import admin

from tickets.models import Category, Ticket, TicketComment, TicketStatusHistory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_date")
    search_fields = ("name",)


class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0
    readonly_fields = ("author_name", "comment", "created_date")
    can_delete = False


class TicketStatusHistoryInline(admin.TabularInline):
    model = TicketStatusHistory
    extra = 0
    readonly_fields = ("old_status", "new_status", "created_date")
    can_delete = False


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "priority", "category", "assigned_to", "created_date")
    list_filter = ("status", "priority", "category", "assigned_to")
    search_fields = ("title", "description", "reporter_name")
    inlines = [TicketStatusHistoryInline, TicketCommentInline]
