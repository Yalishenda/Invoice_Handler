from datetime import datetime


def read_booking(page: dict):
    booking = Reservation()
    try:
        booking.page_id = page['id']
        props = page['properties']
        booking.url = page['url']
        booking.booking_num = props['booking_num']['title'][0]['text']['content']
        booking.order_limit = float(props['order_limit']['number'])
        booking.res_date = datetime.fromisoformat(props['date']['date']['start'])
        booking.total_w_vat = float(props['total_with_vat']['number'])
        booking.status = props['status']['status']['name']
        booking.faculty = props['faculty']['select']['name']
        booking.invoice_num = props['invoice_num']['number']
        print(f'Booking #{booking.booking_num} read successfully')
    except Exception as e:
        print(f'Unable to read page:\n{e}')
     #   print(page)
    return booking


class Reservation:
    def __init__(self, booking_num: str = '',
                 faculty: str = '',
                 order_limit: float | None = 0.0,
                 status: str = '',
                 res_date: datetime.date = datetime.today(),
                 total_w_vat: float | None = None,
                 seats_num: int | None = None,
                 page_id: str | None = None,
                 invoice_num: str | None = None,
                 url: str | None = None,
                 ):
        self.booking_num = booking_num
        self.status = status
        self.faculty = faculty
        self.order_limit = order_limit
        self.total_w_vat = total_w_vat
        self.invoice_num = invoice_num
        self.seats_num = seats_num
        self.page_id = page_id
        self.res_date = res_date
        self.url = url

    def __str__(self):
        text = f'Booking #{self.booking_num} at {self.res_date}, {self.status}'
        return text

    def __repr__(self):
        text = f'Booking #{self.booking_num}\nStatus: {self.status}\nDate: {self.res_date}\n' \
               f'{self.seats_num} seats for {self.order_limit} NIS limit\n' \
               f'Faculty: {self.faculty}\n' \
               f'url: {self.url}'
        return text
