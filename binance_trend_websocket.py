from binance_indicators_websocket import IndicatorWebsocket


def get_trend_with_p1_p2_p3(trend, price_current, price_previous, counter_down_up, counter_changes, price_change):
    trend_p1, difference = IndicatorWebsocket.tolerance(trend, price_current, price_previous)
    trend_p2, counter_down_up = IndicatorWebsocket.max_counts(trend, price_current, price_previous, counter_down_up)
    trend_p3, difference_change = IndicatorWebsocket.tolerance_change(trend, price_current, price_change)

    print('\n\tPrice(p): %f \t Price(curr): %f \t Diff: %f \t CDown: %i \t CUp: %i \t Price(change): %f \t'
          ' Diff(change): %f' % (price_previous, price_current, difference, counter_down_up[0],
                                 counter_down_up[1], price_change, difference_change))

    # Verifica se a tendência mudou.
    if (trend_p1 != trend or trend_p2 != trend) and trend_p3 != trend:
        is_change = True
        trend_current = not trend
        counter_changes += 1

        # Printar se houver indicação forte de mudança, ou seja, indicação de tolerance e max_counts.
        if trend_p1 != trend and trend_p2 != trend:
            print('\n\t=== [Indicação forte de mudança!]', end='\n')

        # Printar dados de mudança.
        if trend:   # UP
            print('\n\t=== (Diff: %f, CDown: %i, Change: %ith)' %
                  (difference, counter_down_up[0], counter_changes), end='\n')
        else:       # DOWN
            print('\n\t=== (Diff: %f, CUp: %i, Change: %ith)' %
                  (difference, counter_down_up[1], counter_changes), end='\n')

        # Resetar contadores.
        counter_down_up[0] = 0
        counter_down_up[1] = 0

    else:
        is_change = False
        trend_current = trend

    return trend_current, is_change, counter_down_up, counter_changes


def get_trend_trandingview_summary(trend, price_current, price_previous, counter_down_up, counter_changes,
                                   price_change):
    trend_p1, recommend_summary = IndicatorWebsocket.tradingview_alerts(trend)
    trend_p2, counter_down_up = IndicatorWebsocket.max_counts(trend, price_current, price_previous, counter_down_up)
    trend_p3, difference_change = IndicatorWebsocket.tolerance_change(trend, price_current, price_change)

    print('\nR. Summary: %s \t Price(p): %f \t Price(curr): %f \t CDown: %i \t CUp: %i \t Price(change): %f \t'
          ' Diff(change): %f' % (recommend_summary, price_previous, price_current, counter_down_up[0],
                                 counter_down_up[1], price_change, difference_change))

    # Verifica se a tendência mudou.
    if (trend_p1 != trend or trend_p2 != trend) and trend_p3 != trend:
        is_change = True
        trend_current = not trend
        counter_changes += 1

        # Printar se houver indicação forte de mudança, ou seja, indicação de TrandingView e max_counts.
        if trend_p1 != trend and trend_p2 != trend:
            print('\n\t=== [Indicação forte de mudança!]', end='\n')

        # Printar dados de mudança.
        if trend:   # UP
            print('\n\t=== (Recommendation (summary): %s, CDown: %i, Change: %ith)' %
                  (recommend_summary, counter_down_up[0], counter_changes), end='\n')
        else:       # DOWN
            print('\n\t=== (Recommendation (summary): %s, CUp: %i, Change: %ith)' %
                  (recommend_summary, counter_down_up[1], counter_changes), end='\n')

        # Resetar contadores.
        counter_down_up[0] = 0
        counter_down_up[1] = 0

    else:
        is_change = False
        trend_current = trend

    return trend_current, is_change, counter_down_up, counter_changes
