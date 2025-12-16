```mermaid
architecture-beta
    group themona(mdi:alert-circle-check-outline)[The Mona]
    group buttons(mdi:alert-circle-check-outline)[Buttons] in themona

    service button(server)[Button_X] in buttons

    service controller(server)[Controller] in themona
    service ledstrip(server)[Ledstrips] in themona

    controller:B <-[wireless]-> T:button
    controller:T -- B:ledstrip
 