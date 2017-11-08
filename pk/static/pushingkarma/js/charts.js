/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

pk.charts = {

  budget_trend: function(data) {
    // https://api.highcharts.com/highstock/plotOptions.column
    var chart = {};
    pk.utils.rset(chart, 'chart.backgroundColor', '#0000000a');
    pk.utils.rset(chart, 'chart.height', 18);
    pk.utils.rset(chart, 'chart.width', 53);
    pk.utils.rset(chart, 'chart.margin', [0, 2, 0, 2]);
    pk.utils.rset(chart, 'chart.spacing', 0);
    pk.utils.rset(chart, 'chart.type', 'column');
    pk.utils.rset(chart, 'credits.enabled', false);
    pk.utils.rset(chart, 'exporting.enabled', null);
    pk.utils.rset(chart, 'legend.enabled', false);
    pk.utils.rset(chart, 'plotOptions.column.borderWidth', 0);
    pk.utils.rset(chart, 'plotOptions.column.color', '#888');
    pk.utils.rset(chart, 'plotOptions.column.enableMouseTracking', false);
    pk.utils.rset(chart, 'plotOptions.column.minPointLength', 2);
    pk.utils.rset(chart, 'plotOptions.column.pointPadding', 0.02);
    pk.utils.rset(chart, 'plotOptions.column.pointWidth', 3);
    pk.utils.rset(chart, 'title.text', null);
    pk.utils.rset(chart, 'xAxis.labels.enabled', false);
    pk.utils.rset(chart, 'xAxis.lineWidth', 0);
    pk.utils.rset(chart, 'xAxis.tickLength', 0);
    pk.utils.rset(chart, 'yAxis.endOnTick', false);
    pk.utils.rset(chart, 'yAxis.gridLineWidth', 0);
    pk.utils.rset(chart, 'yAxis.labals.enabled', false);
    pk.utils.rset(chart, 'yAxis.title.enabled', false);
    chart.series = [{data: data}];
    return chart;
  },

};
