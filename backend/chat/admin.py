from django.contrib import admin
from .models import AIChatSession, ChatInteraction

# Customize Admin Site
admin.site.site_header = "Asistente Comercial Sogacsa-Linde Login"
admin.site.site_title = "Asistente Comercial Sogacsa-Linde Admin"
admin.site.index_title = "Welcome to Asistente Comercial Sogacsa-Linde"

class ChatInteractionInline(admin.TabularInline):
    model = ChatInteraction
    extra = 0
    readonly_fields = ('timestamp',)

@admin.register(AIChatSession)
class AIChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'summary', 'is_deleted')
    list_filter = ('user', 'is_deleted', 'created_at')
    search_fields = ('summary', 'id', 'user__username')
    inlines = [ChatInteractionInline]

@admin.register(ChatInteraction)
class ChatInteractionAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'is_user', 'timestamp', 'message_snippet')
    list_filter = ('is_user', 'timestamp')
    search_fields = ('message',)

    def message_snippet(self, obj):
        return obj.message[:50]
