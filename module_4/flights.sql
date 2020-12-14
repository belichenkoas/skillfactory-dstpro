WITH aaq_flights AS
  (SELECT *,
          actual_departure - scheduled_departure AS time_wait, -- задержка
          actual_arrival - actual_departure time_flight -- время полёта
   FROM dst_project.flights
   WHERE departure_airport = 'AAQ'
     AND (date_trunc('month', scheduled_departure) in ('2017-01-01',
                                                       '2017-02-01',
                                                       '2017-12-01'))
     AND status not in ('Cancelled')
     AND arrival_airport != 'NOZ' -- данные о посадочных отстутсвуют
),
  seats_count AS
  (SELECT aircraft_code,
          count(seat_no) AS capacity -- количество мест в самолете
   FROM dst_project.seats
   GROUP BY aircraft_code
),
  passes AS
  (SELECT bp.flight_id,
          count(bp.seat_no) AS seat_pass  -- количество занятых мест
   FROM dst_project.boarding_passes bp
   WHERE bp.flight_id in
       (SELECT flight_id
        FROM aaq_flights) -- работает быстрее, чем join
   GROUP BY bp.flight_id
),
  sales AS
  (SELECT tf.flight_id,
          sum(tf.amount) total_sales -- сумма проданных билетов
   FROM dst_project.ticket_flights tf
   WHERE tf.flight_id in
       (SELECT flight_id
        FROM aaq_flights) -- работает быстрее, чем join
   GROUP BY tf.flight_id
),
  fuel AS
  (SELECT '733' AS aircraft_code,
          2600 * 47 AS rate -- л/ч расход топлива из открытых источников

   UNION SELECT 'SU9' AS aircraft_code,
                1700 * 47 AS rate -- л/ч * стоимость (руб. среднее) расход топлива из открытых источников
),
  total_fuel AS
  (SELECT flight_id,
          date_part('hour', fl.time_flight) + date_part('min', fl.time_flight)/60 AS flight_hours, -- время полёта в часах
          (date_part('hour', fl.time_flight) + date_part('min', fl.time_flight)/60) * fu.rate AS fuel_price -- затраты на топливо
   FROM aaq_flights AS fl
   LEFT JOIN fuel AS fu ON fl.aircraft_code = fu.aircraft_code
)
SELECT fl.flight_id, -- идентификатор рейса
       fl.flight_no, -- номер рейса
       apd.city AS departure_city, -- город вылета
       fl.scheduled_departure, -- время вылета по расписанию
       fl.arrival_airport, -- аэропорт прибытия
       apa.city AS arrival_city, -- город прибытия
       ac.model,  -- модель самолёта
       date_part('hour', fl.time_wait)*60 + date_part('min', fl.time_wait) AS wait_min, -- задержка (в минутах)
       tf.flight_hours, -- время полёта (в часах)
       sc.capacity , -- вместимость самолёта
       ps.seat_pass, -- занятые места
       sc.capacity - ps.seat_pass free_seats, -- свободные места
       sl.total_sales, -- суммарная стоимость проданных билетов
       tf.fuel_price, -- стоимость топлива
       sl.total_sales - tf.fuel_price profit -- доход
FROM aaq_flights fl
LEFT JOIN seats_count sc ON fl.aircraft_code = sc.aircraft_code
LEFT JOIN passes ps ON fl.flight_id = ps.flight_id
LEFT JOIN sales sl ON fl.flight_id = sl.flight_id
LEFT JOIN total_fuel AS tf ON fl.flight_id = tf.flight_id
LEFT JOIN dst_project.aircrafts ac ON fl.aircraft_code = ac.aircraft_code
LEFT JOIN dst_project.airports apd ON fl.departure_airport = apd.airport_code
LEFT JOIN dst_project.airports apa ON fl.arrival_airport = apa.airport_code
ORDER BY profit ASC;
