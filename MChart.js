/*
* https://github.com/monkeymia/
*
* Copyright (c) 2014, monkeymia, All rights reserved.
*
* This library is free software; you can redistribute it and/or
* modify it under the terms of the GNU Lesser General Public
* License as published by the Free Software Foundation; either
* version 3.0 of the License, or (at your option) any later version.
*
* This library is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
* Lesser General Public License for more details.
*
* You should have received a copy of the GNU Lesser General Public
* License along with this library
*
*/

MChart = (function (canvas_id) {
	var ctx;
    var cur_max_x_value = 0;
    var cur_max_y_value = 0;
    var height          = 0;
    var width           = 0;
	var datasets        = []  //	{ color  : "#00FF00", values : []}
	
	ctx = document.getElementById(canvas_id).getContext("2d");
	width           = ctx.canvas.width;
	height          = ctx.canvas.height;
	cur_max_x_value = width;
	/* public functions */
    var mchart = 
		{	draw            : draw
		,   clear           : clear
        ,   generateLegend  : generateLegend
        ,   as_csv          : as_csv
		,   set_max_x_value : function (x) {cur_max_x_value = x;}
		,   set_max_y_value : function (y) {cur_max_y_value = y;}
		,   append_dataset  : function (ds) {datasets.push (ds);}
		,   prepend_dataset : function (ds) {datasets.unshift (ds);}
		,   rm_dataset      : function (ds) {datasets.pop ();}
		,   shift_dataset   : function (ds) {datasets.shift ();}
		,   append_value    : function (dsi, val) 
				{ datasets [dsi].values.push (val);
				  if (val > cur_max_y_value) {cur_max_y_value = val;};
				}
		,  	chart_recorder_add : function (dsi, val) 
				{ datasets [dsi].values.push (val);
				  if (val > cur_max_y_value) {cur_max_y_value = val;};
				  if (datasets [dsi].values.length > cur_max_x_value) {datasets [dsi].values.shift ();};
				}
		,   preappend_value : function (dsi, val) 
				{ datasets [dsi].values.unshift (val);
				  if (val > cur_max_y_value) {cur_max_y_value = val;};
				}
		,   rm_value        : function (dsi) {datasets [dsi].values.pop (val);}
		,   shift_value     : function (dsi) {datasets [dsi].values.shift (val);}
        ,   clear_value     : function (dsi) {datasets [dsi].values = [];}
		};
    return mchart;
	
    function clear ()
	{
		ctx.clearRect (0 , 0 , width , height);
	}

    function as_csv ()
	{
        var i;
        var j;
        var text;
        text = "";
        if (datasets.length == 0)
        {
            return text;
        }
	    for (i = 0; i < datasets.length; i++)
	    {
			dataset = datasets [i];
            text += "\"" + dataset.label + "\",";
        }
        text += "\r\n";
        dataset = datasets [0];
	    for (j = 0; j < dataset.values.length; j++)
	    {
		    for (i = 0; i < datasets.length; i++)
		    {
                text += "\"" + dataset.values[j] + "\",";
            }
            text += "\r\n";
        }
        return text;
	}

    function generateLegend ()
	{
        var i;
        var text;
        text = "<ul>";
		for (i = 0; i < datasets.length; i++)
		{
			dataset = datasets [i];
            text += "<li><span style=\"background-color:";
            text += dataset.color;
            text += "\">";
            text += dataset.label;
            text += "</span></li>";
        }
        text += "</ul>";
        return text;
	}
	
    function draw ()
	{
		var new_max_y_value;
		ctx.clearRect (0 , 0 , width , height);
		draw_scale (cur_max_x_value, cur_max_y_value);
		new_max_y_value = draw_datasets (cur_max_x_value, cur_max_y_value);
		if (new_max_y_value > cur_max_y_value)
		{
			cur_max_y_value = new_max_y_value;
		}
	}
	
    function draw_datasets (max_x, max_y)
    {
		var i; 
		var j; 
		var dataset; 
		var x; 
		var y; 
		var r;
		var v;
		var new_max_y_value;
		var new_max_x_value;
        step_val_y = max_y / (height  - 15);
        step_val_x = max_x / (width  - 70);
		if ((step_val_y < 3) || (step_val_x < 3))
		{
			r = 1;
		}
		else 
		{
			r = 3;
		}
		ctx.lineWidth   = 1;
		ctx.strokeStyle = '#736F6E';  // grey
		new_max_x_value = 0;
		new_max_y_value = 0;
		for (i = 0; i < datasets.length; i++)
		{
			dataset = datasets [i];
			ctx.strokeStyle = dataset.color;
//			ctx.fillStyle   = dataset.color;
		    ctx.beginPath();
		    ctx.moveTo (70 + 0, (height - 15) - 0);
		    for (j = 0; j < dataset.values.length; j++)
		    {
			    x = (((width  - 70) / max_x) * j);
			    v = dataset.values[j];
			    if (v < 0) 
			    { 
				    v = 0;
			    }
			    if (v > new_max_y_value)
			    { 
				    new_max_y_value = v;
			    }
			    if (j > new_max_x_value)
			    { 
				    new_max_x_value = j;
			    }
			    y = ((height - 15) / max_y * v)|0;
                if (r < 3)
                {
				    ctx.lineTo(70 + x, (height - 15) - y);
    			}
                else
                {
				    ctx.arc(70 + x, (height - 15) - y, r, 0 , 2 * Math.PI);
    			}
			}
			ctx.stroke();
		}
		return new_max_y_value;
    };
	
    function draw_scale (max_x, max_y)
    {
        var step_p;
        var step_val;
        var y;
        var y_val;
		var number_ticks;
		number_ticks      = 4;
		ctx.lineWidth     = 1;
        step_px  = (height  - 15) / number_ticks;
        step_px |= 0;   // int is faster than sub-pixel drawings 
        if (step_px < 15)
        {
            step_px = 15;
        }
		/* precise but look bad */ 
        /* step_val = max_y / (height  - 15)  * step_px; */ 
        step_val = max_y / number_ticks;
		y_val    = 0;
		ctx.lineWidth   = 1;
		ctx.strokeStyle = '#736F6E';  // grey
		ctx.fillStyle   = '#736F6E';
		ctx.beginPath();
		/* y label */ 
        for (y = (height  - 15); y >= 0; y -= step_px)
        {
            ctx.font = "10px Arial";
			if (y < 10) 
			{
				ctx.fillText (y_val.toPrecision(10), 1 , y + 10);
			}
			else 
			{
				ctx.fillText (y_val.toPrecision(10), 1 , y + 5);
			}
			y_val    += step_val;
        }
		ctx.stroke();
		ctx.strokeStyle = '#E5E4E2';  // platium
		ctx.fillStyle   = '#E5E4E2';
		ctx.beginPath();
        for (y = (height  - 15); y >= 0; y -= step_px)
        {
			ctx.moveTo(70, y);
			ctx.lineTo(width, y);
			y_val    += step_val;
        }
		ctx.stroke();
		/* X Axis */ 
		number_ticks  = 6;
        step_px  = (width  - 70) / number_ticks;
        step_px |= 0;   // int is faster than sub-pixel drawings 
        if (step_px < 15)
        {
            step_px = 15;
        }
        step_val = max_x / number_ticks;
		y_val    = 0;
		ctx.strokeStyle = '#736F6E';  // grey
		ctx.fillStyle   = '#736F6E';
		ctx.beginPath();
		/* y label */ 
        for (y = 70; y < (width  + 1); y += step_px)
        {
            ctx.font = "10px Arial";
			if (y > (width  - step_px + 1)) 
			{
				ctx.fillText (y_val.toPrecision(4), y - step_px + ((step_px / 2)|0), height - 1);
			}
			else 
			{
				ctx.fillText (y_val.toPrecision(4), y , height - 1);
			}
			y_val    += step_val;
        }
		ctx.stroke();
		ctx.strokeStyle = '#E5E4E2';  // platium
		ctx.fillStyle   = '#E5E4E2';
		ctx.beginPath();
        for (y = 70; y < (width  + 1); y += step_px)
        {
			ctx.moveTo(y, height);
			ctx.lineTo(y, 0);
			y_val    += step_val;
        }
		ctx.stroke();
    };
});
