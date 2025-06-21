from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth import get_user_model
from apps.usuarios.models import Asesor, Aprendiz
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

def send_welcome_email(user, password=None):
    """
    Send welcome email to new users with enhanced functionality
    
    Args:
        user: User object
        password: Optional password to include in email (for system-generated passwords)
    """
    try:
        subject = '¡Bienvenido a S&S Asesorías Virtuales! - Tu cuenta ha sido creada exitosamente'
        
        # Prepare context for template
        context = {
            'user': user,
            'role': user.get_role_display() if hasattr(user, 'get_role_display') else user.role,
            'password': password,  # Will be None if user chose their own password
            'site_name': 'S&S Asesorías Virtuales',
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
            'login_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/usuarios/login/"
        }
        
        html_content = render_to_string('emails/welcome.html', context)
        text_content = strip_tags(html_content)
        
        # Create email message
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
            reply_to=[settings.DEFAULT_FROM_EMAIL] if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None
        )
        msg.attach_alternative(html_content, "text/html")
        
        # Send email
        result = msg.send()
        
        if result:
            logger.info(f"Welcome email sent successfully to {user.email}")
            return True
        else:
            logger.error(f"Failed to send welcome email to {user.email}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending welcome email to {user.email}: {str(e)}")
        return False

def send_group_assignment_email(asesor, grupo):
    """Send email to advisor when assigned to a group"""
    try:
        subject = f'Asignación de Grupo: {grupo.nombre}'
        html_content = render_to_string('emails/group_assignment.html', {
            'asesor': asesor,
            'grupo': grupo,
            'aprendices': grupo.aprendices.all()
        })
        text_content = strip_tags(html_content)
        
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [asesor.usuario.email]
        )
        msg.attach_alternative(html_content, "text/html")
        result = msg.send()
        
        if result:
            logger.info(f"Group assignment email sent successfully to {asesor.usuario.email}")
            return True
        else:
            send_error_report(
                subject='Fallo en envío de asignación de grupo',
                message=f'No se pudo enviar el correo de asignación de grupo: {grupo.nombre}',
                extra_data={'asesor': asesor.usuario.email, 'grupo_id': grupo.id}
            )
            return False
            
    except Exception as e:
        error_msg = f"Error sending group assignment email: {str(e)}"
        logger.error(error_msg)
        send_error_report(
            subject='Error en envío de asignación de grupo',
            message=error_msg,
            extra_data={'asesor': asesor.usuario.email, 'grupo_id': grupo.id if hasattr(grupo, 'id') else 'N/A'}
        )
        return False

def send_meeting_link_email(reunion):
    """Send meeting link to participants"""
    try:
        subject = f'Link de Reunión: {reunion.titulo}'
        html_content = render_to_string('emails/meeting_link.html', {
            'reunion': reunion,
            'link': reunion.link_reunion
        })
        text_content = strip_tags(html_content)
        
        # Get all participant emails
        participant_emails = [participante.usuario.email for participante in reunion.participantes.all()]
        
        if not participant_emails:
            send_error_report(
                subject='No hay participantes para enviar link de reunión',
                message=f'No se encontraron participantes para enviar link de reunión: {reunion.titulo}',
                extra_data={'reunion_id': reunion.id}
            )
            return False
        
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            participant_emails
        )
        msg.attach_alternative(html_content, "text/html")
        result = msg.send()
        
        if result:
            logger.info(f"Meeting link sent successfully to {len(participant_emails)} participants")
            return True
        else:
            send_error_report(
                subject='Fallo en envío de link de reunión',
                message=f'No se pudo enviar el link de reunión: {reunion.titulo}',
                extra_data={'reunion_id': reunion.id, 'destinatarios': participant_emails}
            )
            return False
            
    except Exception as e:
        error_msg = f"Error sending meeting link: {str(e)}"
        logger.error(error_msg)
        send_error_report(
            subject='Error en envío de link de reunión',
            message=error_msg,
            extra_data={'reunion_id': reunion.id if hasattr(reunion, 'id') else 'N/A'}
        )
        return False

def send_test_notification(prueba):
    """Send notification for new test"""
    try:
        subject = f'Nueva Prueba: {prueba.titulo}'
        html_content = render_to_string('emails/test_notification.html', {
            'prueba': prueba,
            'grupo': prueba.grupo
        })
        text_content = strip_tags(html_content)
        
        # Get all student emails in the group
        student_emails = [aprendiz.usuario.email for aprendiz in prueba.grupo.aprendices.all()]
        
        if not student_emails:
            send_error_report(
                subject='No hay aprendices para notificar nueva prueba',
                message=f'No se encontraron aprendices para enviar notificación de nueva prueba: {prueba.titulo}',
                extra_data={'prueba_id': prueba.id, 'grupo': prueba.grupo.nombre}
            )
            return False
        
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            student_emails
        )
        msg.attach_alternative(html_content, "text/html")
        result = msg.send()
        
        if result:
            logger.info(f"Test notification sent successfully to {len(student_emails)} students")
            return True
        else:
            send_error_report(
                subject='Fallo en envío de notificación de nueva prueba',
                message=f'No se pudo enviar la notificación de nueva prueba: {prueba.titulo}',
                extra_data={'prueba_id': prueba.id, 'destinatarios': student_emails}
            )
            return False
            
    except Exception as e:
        error_msg = f"Error sending test notification: {str(e)}"
        logger.error(error_msg)
        send_error_report(
            subject='Error en envío de notificación de nueva prueba',
            message=error_msg,
            extra_data={'prueba_id': prueba.id if hasattr(prueba, 'id') else 'N/A'}
        )
        return False

def send_account_blocked_email(user):
    """Send email to user when their account is blocked"""
    try:
        subject = 'Cuenta bloqueada - S&S Asesorías Virtuales'
        html_content = render_to_string('emails/account_blocked.html', {'user': user})
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return True
    except Exception as e:
        logger.error(f"Error sending account blocked email: {str(e)}")
        return False

def send_error_report(subject, message, extra_data=None):
    """
    Envía un correo de reporte de error a los administradores del sistema.
    """
    try:
        admin_emails = [admin.email for admin in User.objects.filter(is_superuser=True)]
        if not admin_emails:
            logger.warning("No superusers found to send error report.")
            return False

        full_message = message
        if extra_data:
            full_message += '\n\nDatos adicionales:\n' + str(extra_data)
        
        send_mail(
            subject=f'[S&S Asesorías] {subject}',
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            fail_silently=False,
        )
        logger.info(f"Reporte de error enviado a {', '.join(admin_emails)}")
        return True
    except Exception as e:
        logger.error(f"Error enviando reporte de error: {str(e)}")
        return False

def send_mass_email(subject, html_template, context, recipient_emails, email_type="general"):
    """
    Envía correos masivos con manejo robusto de errores y reportes.
    
    Args:
        subject: Asunto del correo
        html_template: Template HTML a usar
        context: Contexto para el template
        recipient_emails: Lista de correos destinatarios
        email_type: Tipo de correo para el reporte (ej: "notificacion", "anuncio", etc.)
    
    Returns:
        dict: {'success': bool, 'sent': int, 'failed': int, 'errors': list}
    """
    if not recipient_emails:
        send_error_report(
            subject=f'No hay destinatarios para envío masivo de {email_type}',
            message=f'No se encontraron destinatarios para enviar: {subject}',
            extra_data={'tipo': email_type, 'asunto': subject}
        )
        return {'success': False, 'sent': 0, 'failed': 0, 'errors': ['No hay destinatarios']}
    
    try:
        html_content = render_to_string(html_template, context)
        text_content = strip_tags(html_content)
        
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            recipient_emails
        )
        msg.attach_alternative(html_content, "text/html")
        result = msg.send()
        
        if result:
            logger.info(f"Mass email sent successfully to {len(recipient_emails)} recipients")
            return {'success': True, 'sent': len(recipient_emails), 'failed': 0, 'errors': []}
        else:
            send_error_report(
                subject=f'Fallo en envío masivo de {email_type}',
                message=f'No se pudo enviar el correo masivo: {subject}',
                extra_data={'tipo': email_type, 'destinatarios': len(recipient_emails)}
            )
            return {'success': False, 'sent': 0, 'failed': len(recipient_emails), 'errors': ['Fallo en envío']}
            
    except Exception as e:
        error_msg = f"Error sending mass email: {str(e)}"
        logger.error(error_msg)
        send_error_report(
            subject=f'Error en envío masivo de {email_type}',
            message=error_msg,
            extra_data={'tipo': email_type, 'asunto': subject, 'destinatarios': len(recipient_emails)}
        )
        return {'success': False, 'sent': 0, 'failed': len(recipient_emails), 'errors': [str(e)]}

def send_bulk_notifications(notifications, notification_type="general"):
    """
    Envía notificaciones masivas con reporte de errores.
    
    Args:
        notifications: Lista de notificaciones a enviar
        notification_type: Tipo de notificación para el reporte
    
    Returns:
        dict: Resumen del envío
    """
    if not notifications:
        send_error_report(
            subject=f'No hay notificaciones para enviar de tipo {notification_type}',
            message=f'No se encontraron notificaciones para enviar',
            extra_data={'tipo': notification_type}
        )
        return {'success': False, 'sent': 0, 'failed': 0, 'errors': ['No hay notificaciones']}
    
    sent_count = 0
    failed_count = 0
    errors = []
    
    for notification in notifications:
        try:
            # Aquí puedes personalizar según el tipo de notificación
            if hasattr(notification, 'usuario') and hasattr(notification.usuario, 'email'):
                recipient_email = notification.usuario.email
                subject = f"Notificación: {getattr(notification, 'titulo', 'Nueva notificación')}"
                
                context = {
                    'notification': notification,
                    'user': notification.usuario
                }
                
                result = send_mass_email(
                    subject=subject,
                    html_template='emails/notification.html',
                    context=context,
                    recipient_emails=[recipient_email],
                    email_type=notification_type
                )
                
                if result['success']:
                    sent_count += 1
                else:
                    failed_count += 1
                    errors.extend(result['errors'])
            else:
                failed_count += 1
                errors.append(f'Notificación sin usuario válido: {notification}')
                
        except Exception as e:
            failed_count += 1
            errors.append(str(e))
    
    # Reportar resumen si hay errores
    if failed_count > 0:
        send_error_report(
            subject=f'Errores en envío masivo de {notification_type}',
            message=f'Se enviaron {sent_count} notificaciones, fallaron {failed_count}',
            extra_data={'tipo': notification_type, 'enviadas': sent_count, 'fallidas': failed_count, 'errores': errors[:5]}
        )
    
    return {
        'success': failed_count == 0,
        'sent': sent_count,
        'failed': failed_count,
        'errors': errors
    }

def send_asesoria_change_notification(asesoria, change_type, old_data=None):
    """
    Send notification when an asesoria is modified (date, time, or cancelled)
    
    Args:
        asesoria: Asesoria object
        change_type: 'date_change', 'time_change', 'cancelled', 'created'
        old_data: Dictionary with old values (for date/time changes)
    """
    try:
        # Determine subject and template based on change type
        if change_type == 'date_change':
            subject = f'Cambio de Fecha - Asesoría: {asesoria.componente.nombre}'
            template = 'emails/asesoria_date_change.html'
        elif change_type == 'time_change':
            subject = f'Cambio de Hora - Asesoría: {asesoria.componente.nombre}'
            template = 'emails/asesoria_time_change.html'
        elif change_type == 'cancelled':
            subject = f'Asesoría Cancelada: {asesoria.componente.nombre}'
            template = 'emails/asesoria_cancelled.html'
        elif change_type == 'created':
            subject = f'Nueva Asesoría Programada: {asesoria.componente.nombre}'
            template = 'emails/asesoria_created.html'
        else:
            subject = f'Actualización de Asesoría: {asesoria.componente.nombre}'
            template = 'emails/asesoria_updated.html'
        
        # Prepare context
        context = {
            'asesoria': asesoria,
            'grupo': asesoria.grupo,
            'asesor': asesoria.grupo.asesor,
            'componente': asesoria.componente,
            'change_type': change_type,
            'old_data': old_data,
            'site_name': 'S&S Asesorías Virtuales',
        }
        
        html_content = render_to_string(template, context)
        text_content = strip_tags(html_content)
        
        # Get recipient emails (aprendices + asesor)
        recipient_emails = [aprendiz.usuario.email for aprendiz in asesoria.grupo.aprendices.all()]
        if asesoria.grupo.asesor:
            recipient_emails.append(asesoria.grupo.asesor.usuario.email)
        
        if not recipient_emails:
            logger.warning(f"No recipients found for asesoria change notification: {asesoria.id}")
            return False
        
        # Send email
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_emails,
            reply_to=[settings.DEFAULT_FROM_EMAIL] if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None
        )
        msg.attach_alternative(html_content, "text/html")
        
        result = msg.send()
        
        if result:
            logger.info(f"Asesoria {change_type} notification sent successfully to {len(recipient_emails)} recipients")
            return True
        else:
            logger.error(f"Failed to send asesoria {change_type} notification")
            return False
            
    except Exception as e:
        logger.error(f"Error sending asesoria {change_type} notification: {str(e)}")
        return False

def send_welcome_email_aprendiz(aprendiz, password=None):
    """
    Send specialized welcome email for aprendices
    """
    try:
        subject = '¡Bienvenido a S&S Asesorías Virtuales! - Tu cuenta de Aprendiz ha sido creada'
        
        context = {
            'user': aprendiz.usuario,
            'aprendiz': aprendiz,
            'role': 'Aprendiz',
            'password': password,
            'site_name': 'S&S Asesorías Virtuales',
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
            'login_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/usuarios/login/",
            'dashboard_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/usuarios/aprendiz/dashboard/",
            'componentes_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/usuarios/aprendiz/seleccionar-componentes/"
        }
        
        html_content = render_to_string('emails/welcome_aprendiz.html', context)
        text_content = strip_tags(html_content)
        
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[aprendiz.usuario.email],
            reply_to=[settings.DEFAULT_FROM_EMAIL] if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None
        )
        msg.attach_alternative(html_content, "text/html")
        
        result = msg.send()
        
        if result:
            logger.info(f"Welcome email sent successfully to aprendiz {aprendiz.usuario.email}")
            return True
        else:
            logger.error(f"Failed to send welcome email to aprendiz {aprendiz.usuario.email}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending welcome email to aprendiz {aprendiz.usuario.email}: {str(e)}")
        return False

def send_welcome_email_asesor(asesor, password=None):
    """
    Send specialized welcome email for asesores
    """
    try:
        subject = '¡Bienvenido a S&S Asesorías Virtuales! - Tu cuenta de Asesor ha sido creada'
        
        context = {
            'user': asesor.usuario,
            'asesor': asesor,
            'role': 'Asesor',
            'password': password,
            'site_name': 'S&S Asesorías Virtuales',
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
            'login_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/usuarios/login/",
            'dashboard_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/usuarios/asesor/dashboard/",
            'grupos_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/grupos/asesor/"
        }
        
        html_content = render_to_string('emails/welcome_asesor.html', context)
        text_content = strip_tags(html_content)
        
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[asesor.usuario.email],
            reply_to=[settings.DEFAULT_FROM_EMAIL] if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None
        )
        msg.attach_alternative(html_content, "text/html")
        
        result = msg.send()
        
        if result:
            logger.info(f"Welcome email sent successfully to asesor {asesor.usuario.email}")
            return True
        else:
            logger.error(f"Failed to send welcome email to asesor {asesor.usuario.email}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending welcome email to asesor {asesor.usuario.email}: {str(e)}")
        return False

def send_asesoria_reminder(asesoria):
    """
    Send reminder email for upcoming asesoria
    """
    try:
        subject = f'Recordatorio - Asesoría mañana: {asesoria.componente.nombre}'
        
        context = {
            'asesoria': asesoria,
            'grupo': asesoria.grupo,
            'asesor': asesoria.grupo.asesor,
            'componente': asesoria.componente,
            'site_name': 'S&S Asesorías Virtuales',
        }
        
        html_content = render_to_string('emails/asesoria_reminder.html', context)
        text_content = strip_tags(html_content)
        
        # Get recipient emails
        recipient_emails = [aprendiz.usuario.email for aprendiz in asesoria.grupo.aprendices.all()]
        if asesoria.grupo.asesor:
            recipient_emails.append(asesoria.grupo.asesor.usuario.email)
        
        if not recipient_emails:
            logger.warning(f"No recipients found for asesoria reminder: {asesoria.id}")
            return False
        
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_emails,
            reply_to=[settings.DEFAULT_FROM_EMAIL] if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None
        )
        msg.attach_alternative(html_content, "text/html")
        
        result = msg.send()
        
        if result:
            logger.info(f"Asesoria reminder sent successfully to {len(recipient_emails)} recipients")
            return True
        else:
            logger.error(f"Failed to send asesoria reminder")
            return False
            
    except Exception as e:
        logger.error(f"Error sending asesoria reminder: {str(e)}")
        return False 