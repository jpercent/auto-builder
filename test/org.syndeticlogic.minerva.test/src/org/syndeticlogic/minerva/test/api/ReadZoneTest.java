/**
 * 
 */
package org.syndeticlogic.minerva.test.api;

import static org.junit.Assert.*;

import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.syndeticlogic.minerva.api.ReadZone;

public class ReadZoneTest {
	ReadZone rZone;

	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
	}

	@AfterClass
	public static void tearDownAfterClass() throws Exception {
	}

	@Before
	public void setUp() throws Exception {
		rZone = new ReadZone("readerID");
		
	}

	@After
	public void tearDown() throws Exception {
	}

	@Test
	public void testReadZoneString() {
		//fail("Not yet implemented");
	}

	@Test
	public void testReadZoneStringIntegerArray() {
		//fail("Not yet implemented");
	}

	@Test
	public void testReadZoneStringListOfStringBooleanIntegerArray() {
		//fail("Not yet implemented");
	}

	@Test
	public void testCreateReadZone() {
		//fail("Not yet implemented");
	}

	@Test
	public void testGetReaderID() {
		
		rZone.setReaderID("A001");
		assertEquals("A001", rZone.getReaderID());
		
	}
	
	@Test
	public void testIsInclude() {
	//	fail("Not yet implemented");
	}

	@Test
	public void testSetInclude() {
		
		rZone.setInclude(true);
		assertEquals(true, rZone.isInclude());
	}

	@Test
	public void testClone() {
		//fail("Not yet implemented");
	}

}
