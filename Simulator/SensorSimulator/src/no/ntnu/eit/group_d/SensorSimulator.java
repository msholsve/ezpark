package no.ntnu.eit.group_d;


import java.awt.BorderLayout;
import java.awt.FlowLayout;
import java.awt.GridBagLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.IOException;

import javax.swing.*;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;
import org.json.simple.*;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class SensorSimulator extends JFrame {

	
	private JTabbedPane tabPane;
	
	public SensorSimulator() {
		initUI();		
	}
	
	private void initUI() {
		tabPane = new JTabbedPane();
		
        setTitle("Sensor simulator");
        setSize(500, 500);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        
        loadRooms();
        
        
       // tabPane.addTab("Room 1", new Room(10));
        //tabPane.addTab("Room 2", new Room(40));
        //tabPane.addTab("Room 3", new Room(20));
        
        getContentPane().setLayout(new BorderLayout());
        getContentPane().add(tabPane, BorderLayout.CENTER);       
        
        JPanel panel = new JPanel();
        getContentPane().add(panel, BorderLayout.SOUTH);
       
        JButton btnReloadAllRooms = new JButton("Reload all rooms");
        btnReloadAllRooms.addActionListener(new ActionListener() {
        	public void actionPerformed(ActionEvent e) {
        		
        		loadRooms();
        	}
        });
        panel.add(btnReloadAllRooms);
       
    }
	
	public void loadRooms() {
		JSONParser parser = new JSONParser();
        
        try {
			String rooms = HttpHelper.getHttp("http://isit.routable.org/api/rooms");
			
			
			JSONObject obj = (JSONObject)parser.parse(rooms);
			JSONArray jsonArray = (JSONArray)obj.get("_items");
			tabPane.removeAll();
			 
			for(int i = 0; i < jsonArray.size(); i++) {
				
				JSONObject jobj = (JSONObject)jsonArray.get(i);
				String roomName = (String) jobj.get("name");

				jobj = (JSONObject) jobj.get("_links");
				jobj = (JSONObject) jobj.get("self");
				String roomUrl = (String) jobj.get("href");
				tabPane.addTab(roomName, new Room("http://isit.routable.org/api/" + roomUrl));
				
			}
			
		    
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	
	public static void main(String[] args) {
		try {
			UIManager.setLookAndFeel("javax.swing.plaf.metal.MetalLookAndFeel");
		} catch (Throwable e) {
			e.printStackTrace();
		}
		SensorSimulator window = new SensorSimulator();
		window.setVisible(true);
	}
	
}
