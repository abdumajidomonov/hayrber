from odoo import models
from datetime import datetime, time, timedelta
import pytz
import logging

_logger = logging.getLogger(__name__)

TZ = pytz.timezone('Asia/Tashkent')
CHECKOUT_HOUR = 20  # 20:00 Toshkent vaqti


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    def _auto_checkout_open_sessions(self):
        open_records = self.search([('check_out', '=', False)])
        if not open_records:
            _logger.info('Auto checkout: ochiq sessiya topilmadi.')
            return

        count = 0
        for rec in open_records:
            check_in_local = rec.check_in.replace(tzinfo=pytz.utc).astimezone(TZ)
            checkout_naive_local = datetime.combine(check_in_local.date(), time(CHECKOUT_HOUR, 0, 0))
            checkout_utc = TZ.localize(checkout_naive_local).astimezone(pytz.utc).replace(tzinfo=None)

            if rec.check_in >= checkout_utc:
                # Check-in 20:00 dan keyin — 1 daqiqa qo'shamiz
                checkout_utc = rec.check_in.replace(second=0, microsecond=0) + timedelta(minutes=1)

            rec.write({'check_out': checkout_utc})
            count += 1
            _logger.info(
                'Auto checkout: %s (%s) — check_out = %s (UTC)',
                rec.employee_id.name, rec.check_in, checkout_utc,
            )

        _logger.info('Auto checkout: jami %d sessiya yopildi.', count)
