package no.ntnu.eit.group_d;

import java.awt.Color;

import javax.swing.JCheckBox;

import org.json.simple.JSONObject;

public class Seat extends JCheckBox {

	String name;
	String id;
	
	public Seat(JSONObject jsonObj) {
		name = (String)jsonObj.get("name");
		this.setText(name);
		
		if(jsonObj.containsKey("free"))
			setSelected(!(Boolean)jsonObj.get("free"));
		else 
			setEnabled(false);
		
		id = (String)jsonObj.get("_id");
		
		if(this.isSelected()) {
			this.setBackground(Color.PINK);
		}
	}
	
	public String getId() { return this.id; }
}
